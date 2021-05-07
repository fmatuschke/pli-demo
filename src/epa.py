# -*- coding: utf-8 -*-
"""
Analyse Methods for PLI signals
"""

from __future__ import annotations

import numba
import numpy as np
import colorsys


def rot_x(phi: float) -> np.ndarray:
    """ 3d rotation around x-axis: float -> (3,3)-array """
    return np.array(((1, 0, 0), (0, np.cos(phi), -np.sin(phi)),
                     (0, np.sin(phi), np.cos(phi))), float)


def rot_y(phi: float) -> np.ndarray:
    """ 3d rotation around y-axis: float -> (3,3)-array """
    return np.array(((np.cos(phi), 0, np.sin(phi)), (0, 1, 0),
                     (-np.sin(phi), 0, np.cos(phi))), float)


def rot_z(phi: float) -> np.ndarray:
    """ 3d rotation around z-axis: float -> (3,3)-array """
    return np.array(((np.cos(phi), -np.sin(phi), 0),
                     (np.sin(phi), np.cos(phi), 0), (0, 0, 1)), float)


def epa(data: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculates modalities for a PLI image sequence

    Parameters
    ----------
    data : (x,y,rho)-array_like
        rho index must be equidistance between [0,180) degree

    Returns
    -------
    res : transmittance, direction, retardation
    """

    data = np.array(data, copy=False)
    n = data.shape[-1]

    dtype = np.float32 if data.itemsize <= 4 else np.float64
    rho_2 = 2 * np.linspace(0, np.pi, n, False, dtype=dtype)

    a0 = np.sum(data, -1) / n
    a1 = 2 * np.sum(data * np.sin(rho_2), -1) / n
    b1 = 2 * np.sum(data * np.cos(rho_2), -1) / n

    t = 2 * a0
    d = 0.5 * np.arctan2(-b1, a1) + np.pi
    r = np.sqrt(a1 * a1 + b1 * b1) / (a0 + 1e-16)

    d = d % np.pi

    # TODO: d = 0.5 * np.arctan2(a1, -b1) + np.pi without d = d % np.pi

    return t, d, r


def direction(data: np.ndarray) -> np.ndarray:
    """
    Calculates direction map for a PLI image sequence

    Parameters
    ----------
    data : array_like
        (x,y,rho)-array, rho index must be equidistance between [0,180) degree

    Returns
    -------
    res : direction
    """

    data = np.array(data, copy=False)
    n = data.shape[-1]

    dtype = np.float32 if data.itemsize <= 4 else np.float64
    rho_2 = 2 * np.linspace(0, np.pi, n, False, dtype=dtype)

    a1 = 2 * np.sum(data * np.sin(rho_2), -1) / n
    b1 = 2 * np.sum(data * np.cos(rho_2), -1) / n

    d = 0.5 * np.arctan2(-b1, a1) + np.pi

    d = d % np.pi

    return d


def simple_incl(transmittance: np.ndarray,
                retardation: np.ndarray) -> np.ndarray:

    # ret>1 detected, probably hand movement in front of the camera
    hist, edges = np.histogram(retardation[retardation <= 1], 42)
    hist[hist <= 1] = 0  # erfahrungswert

    threshold = edges[np.argwhere(hist > 0)[-1] + 1]
    # TODO: why not using mask?
    # mask = np.logical_and(retardation > 0.080, retardation <= threshold)

    inclination = np.pi / 2 * (1 - retardation / threshold)
    return inclination


def fom(direction: np.ndarray, inclination: np.ndarray) -> np.ndarray:
    # todo check with numba
    hsv_to_rgb_v = np.vectorize(colorsys.hsv_to_rgb)
    fom = np.dstack(
        hsv_to_rgb_v(direction / np.pi, np.ones_like(direction),
                     1 - (inclination / np.pi * 2)))
    return fom


@numba.njit(cache=True)
def _calc_tilt(x: np.ndarray, y: np.ndarray, z: np.ndarray, rho: float,
               rot: np.ndarray) -> np.ndarray:
    data = np.zeros((x.shape[0], x.shape[1], rho.size))
    incl = np.zeros((x.shape[0], x.shape[1]))
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            # if not mask[i, j]:
            #     continue
            v = np.dot(rot, np.array([x[i, j], y[i, j], z[i, j]]))
            a = np.pi / 2 - np.arccos(v[2])
            p = np.arctan2(v[1], v[0])

            delta = 0.2 * np.cos(a)**2
            data[i, j, :] = (1 + np.sin(2 * (rho - p)) * np.sin(delta))

            incl[i, j] = a
    return data, incl


def calc_tilts(transmittance: np.ndarray, direction: np.ndarray,
               retardation: np.ndarray, inclination: np.ndarray,
               N: int) -> np.ndarray:

    # TODO: speedup
    tilt_frames = []
    x = np.cos(inclination) * np.cos(direction)
    y = np.cos(inclination) * np.sin(direction)
    z = np.sin(inclination)

    theta = np.deg2rad(20)

    tilt_frames = np.empty(
        (4, transmittance.shape[0], transmittance.shape[1], N))
    tilt_transmittance = np.empty(
        (4, transmittance.shape[0], transmittance.shape[1]))
    tilt_direction = np.empty(
        (4, transmittance.shape[0], transmittance.shape[1]))
    tilt_retardation = np.empty(
        (4, transmittance.shape[0], transmittance.shape[1]))
    tilt_inclination = np.empty(
        (4, transmittance.shape[0], transmittance.shape[1]))

    rho = np.linspace(0, np.pi, N, endpoint=False, dtype=x.dtype)
    for r, phi in enumerate([0, 90, 180, 270]):
        rot = np.dot(rot_z(-phi), np.dot(rot_x(theta),
                                         rot_z(phi))).astype(x.dtype)

        frames, tilt_inclination[r] = _calc_tilt(x, y, z, rho, rot)
        tilt_frames[r] = (frames * transmittance[:, :, None]).astype(np.uint8)

    for i, data in enumerate(tilt_frames):
        tilt_transmittance[i], tilt_direction[i], tilt_retardation[i] = epa(
            data)
    return tilt_frames, tilt_transmittance, tilt_direction, tilt_retardation, tilt_inclination
