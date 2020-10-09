import numpy as np
import cv2
import numba

from src import helper


@numba.njit()
def _hsv_black_to_rgb_space(h, s, v):
    # images have to be saved in rgb space

    h = (h + 360) % 360

    hi = np.floor(h / 60)
    f = h / 60.0 - hi

    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))

    if hi == 1:
        r, g, b = q, v, p
    elif hi == 2:
        r, g, b = p, v, t
    elif hi == 3:
        r, g, b = p, q, v
    elif hi == 4:
        r, g, b = t, p, v
    elif hi == 5:
        r, g, b = v, p, q
    else:
        r, g, b = v, t, p

    return np.array((r * 255, g * 255, b * 255), np.uint8)


@numba.njit()
def _orientation_to_hsv(directionValue, inclinationValue):
    h = 360.0 * np.abs(directionValue) / np.pi
    s = 1.0
    v = 1.0 - (2 * np.abs(inclinationValue) / np.pi)

    return _hsv_black_to_rgb_space(h, s, v)


def fom_hsv_black(direction, inclination, mask=None):
    if mask is None:
        mask = np.ones_like(direction, dtype=np.bool)

    hsv = np.zeros((mask.shape[0], mask.shape[1], 3), np.uint8)
    for x in range(mask.shape[0]):
        for y in range(mask.shape[1]):
            if not mask[x, y]:
                continue

            hsv[x, y, :] = _orientation_to_hsv(direction[x, y], inclination[x,
                                                                            y])
    return hsv


class Stack:

    def __init__(self):
        self.n_images = 18
        self.angles = np.linspace(0, np.pi, self.n_images, False)
        self.frames = [None] * self.n_images
        self.coeffs_calced = False
        self.angle_threshold_to_insert = np.deg2rad(2.5)
        self.transmittance = None
        self.direction = None
        self.retardation = None

    def size(self):
        return len([x for x in self.frames if x is not None])

    def full(self):
        return len([None for f in self.frames if f is not None
                   ]) == self.angles.size

    def insert(self, rho, frame):
        # get closest angle
        diff_angles = [
            helper.diff_orientation(rho, target) for target in self.angles
        ]

        if np.min(np.abs(diff_angles)) < self.angle_threshold_to_insert:
            idx = np.argmin(np.abs(diff_angles))
            if self.frames[idx] is None:
                if frame.ndim == 3:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                self.frames[idx] = frame
                return True
        return False

    def fit_pixel(self, x, y):
        pass

    def calc_coeffs(self):
        if len(self.frames) == self.n_images:

            data = np.array(self.frames, np.float32)
            n = data.shape[0]

            rho_2 = 2 * np.linspace(0, np.pi, n, False, dtype=data.dtype)

            a0 = np.sum(data, 0) / n
            a1 = 2 * np.sum(data * np.sin(rho_2)[:, None, None], 0) / n
            b1 = 2 * np.sum(data * np.cos(rho_2)[:, None, None], 0) / n

            self.transmittance = 2 * a0
            self.direction = 0.5 * np.arctan2(-b1, a1) + np.pi
            self.retardation = np.sqrt(a1 * a1 + b1 * b1) / (a0 + 1e-16)
        else:
            print(f"Error, no {self.n_images} mesuered images")

    def calc_fom(self):
        self.inclination = self.retardation / np.amax(self.retardation)
        self.fom = fom_hsv_black(self.direction, self.inclination)

    def clear(self):
        self.frames.clear()
        self.angles.clear()

    def get(self, x, y):
        if self.size() == 0:
            return np.array((0.0)), np.array((0.0))

        angles = [
            self.angles[i] for i, f in enumerate(self.frames) if f is not None
        ]
        angles = np.array(angles)
        frames = [f for f in self.frames if f is not None]
        frames = np.array(frames)
        return angles, frames[:, y, x]
