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


def rot_x(phi):
    """ 3d rotation around x-axis: float -> (3,3)-array """
    return np.array(((1, 0, 0), (0, np.cos(phi), -np.sin(phi)),
                     (0, np.sin(phi), np.cos(phi))), float)


def rot_y(phi):
    """ 3d rotation around y-axis: float -> (3,3)-array """
    return np.array(((np.cos(phi), 0, np.sin(phi)), (0, 1, 0),
                     (-np.sin(phi), 0, np.cos(phi))), float)


def rot_z(phi):
    """ 3d rotation around z-axis: float -> (3,3)-array """
    return np.array(((np.cos(phi), -np.sin(phi), 0),
                     (np.sin(phi), np.cos(phi), 0), (0, 0, 1)), float)


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


def _epa(data):
    data = np.array(data, copy=False)

    n = data.shape[0]
    rho_2 = 2 * np.linspace(0, np.pi, n, False, dtype=data.dtype)

    a0 = np.sum(data, 0) / n
    a1 = 2 * np.sum(data * np.sin(rho_2)[:, None, None], 0) / n
    b1 = 2 * np.sum(data * np.cos(rho_2)[:, None, None], 0) / n

    t = 2 * a0
    d = 0.5 * np.arctan2(-b1, a1) + np.pi
    r = np.sqrt(a1 * a1 + b1 * b1) / (a0 + 1e-16)

    d = d % np.pi

    return t, d, r


@numba.njit(cache=True)
def _calc_tilt(x, y, z, rho, rot, mask):
    data = np.zeros((rho.size, x.shape[0], x.shape[1]))
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            if not mask[i, j]:
                continue
            v = np.dot(rot, np.array([x[i, j], y[i, j], z[i, j]]))
            a = np.pi / 2 - np.arccos(v[2])
            p = np.arctan2(v[1], v[0])

            delta = 0.2 * np.cos(a)**2
            data[:, i, j] = (1 + np.sin(2 * (rho - p)) * np.sin(delta))
    return data


class Stack:

    def __init__(self, ui=None):
        self._ui = ui
        self._n_images = 18
        self._angle_threshold_to_insert = np.deg2rad(2.5)
        self._angles = np.linspace(0, np.pi, self._n_images, False)
        self._frames = [None] * self._n_images
        self._transmittance = None
        self._direction = None
        self._retardation = None
        self._inclination = None
        self._fom = None
        self._mask = None

        self._tilt_mode = 0
        self._tilt_frames = None
        self._tilt_transmittance = None
        self._tilt_direction = None
        self._tilt_retardation = None
        self._tilt_inclination = None

    def set_tilt_mode(self, mode):
        self._tilt_mode = int(mode)

    @property
    def size(self):
        return len([x for x in self._frames if x is not None])

    @property
    def full(self):
        return self.size == self._angles.size

    @property
    def angles(self):
        return np.array([
            self._angles[i] for i, f in enumerate(self._frames) if f is not None
        ])

    @property
    def frames(self):
        return np.array([f for f in self._frames if f is not None])

    def is_analysed(self):
        return self._fom is None

    @property
    def transmittance(self):
        if self._tilt_mode == 0:
            return self._transmittance.copy()
        else:
            return self._tilt_transmittance[self._tilt_mode - 1].copy()

    @property
    def direction(self):
        if self._tilt_mode == 0:
            return self._direction.copy()
        else:
            return self._tilt_direction[self._tilt_mode - 1].copy()

    @property
    def retardation(self):
        if self._tilt_mode == 0:
            return self._retardation.copy()
        else:
            return self._tilt_retardation[self._tilt_mode - 1].copy()

    @property
    def inclination(self):
        return self._inclination.copy()

    @property
    def fom(self):
        return self._fom.copy()

    @property
    def mask(self):
        return self._mask.copy()

    def insert(self, rho, frame):
        # get closest angle
        diff_angles = [
            helper.diff_orientation(rho, target) for target in self._angles
        ]

        is_inserted = False
        if np.min(np.abs(diff_angles)) < self._angle_threshold_to_insert:
            idx = np.argmin(np.abs(diff_angles))
            if self._frames[idx] is None:
                if frame.ndim == 3:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

                frame = cv2.fastNlMeansDenoising(frame, None, 5, 5, 9)
                self._frames[idx] = frame
                is_inserted = True

        if self.full:
            if self._ui is not None:
                self._ui.statusBar().showMessage(f"analysing")
            print("calc_coeffs")
            self.calc_coeffs()
            print("calc_fom")
            self.calc_fom()
            print("calc_tilt")
            self.calc_tilt()
            #
            print("Camera shape:", frame.shape)

        return is_inserted

    def fit_pixel(self, x, y):
        pass

    def calc_coeffs(self):
        if len(self._frames) == self._n_images:
            self._transmittance, self._direction, self._retardation = _epa(
                self.frames.astype(np.float32))
        else:
            print(f"Error, no {self._n_images} measured images")

    def calc_fom(self):
        # ret>1 detected, probably hand movement in front of the camera
        hist, edges = np.histogram(self.retardation[self.retardation <= 1], 42)
        hist[hist <= 1] = 0
        # erfahrungswert. Ich will die einzelenen rauschpixel raus haben

        threshold = edges[np.argwhere(hist > 0)[-1] + 1]
        #print(hist)
        #print(edges)
        #print(threshold)
        self._mask = np.logical_and(self.retardation > 0.080,
                                    self.retardation <= threshold)

        print("Maximal retardation:", np.amax(self._retardation[self._mask]))
        print("Maximal transmittance:", np.amax(self._transmittance))
        self._inclination = np.pi / 2 * (1 - self._retardation / threshold)
        self._fom = fom_hsv_black(self._direction, self._inclination)
        #print(np.shape(self._inclination))
        #print(self._inclination.ndim)
        #print(self._inclination[12][130])
        #np.savetxt("inclinat.txt", self.inclination, fmt="%1.3f")

        from PIL import Image
        im = Image.fromarray(self.retardation)
        im.save('retardation.tif')
        im = Image.fromarray(self._inclination)
        im.save('inclination.tif')
        im = Image.fromarray(self._direction)
        im.save('direction.tif')
        im = Image.fromarray(self._transmittance)
        im.save('transmittance.tif')
        im = Image.fromarray(self._mask)
        im.save('mask.tif')
        im = Image.fromarray(self._fom)
        im.save('fom.tif')

    def calc_tilt(self):
        # TODO: speedup
        self._tilt_frames = []
        x = np.cos(self.inclination) * np.cos(self.direction)
        y = np.cos(self.inclination) * np.sin(self.direction)
        z = np.sin(self.inclination)

        # rho = np.linspace(0, np.pi, 18, endpoint=False)
        theta = np.deg2rad(20)

        self._tilt_frames = [
            np.zeros((18, self._transmittance.shape[0],
                      self._transmittance.shape[1]))
        ] * 4

        rho = np.linspace(0, np.pi, 18, endpoint=False, dtype=x.dtype)
        for r, phi in enumerate([0, 90, 180, 270]):
            rot = np.dot(rot_z(-phi), np.dot(rot_x(theta),
                                             rot_z(phi))).astype(x.dtype)
            self._tilt_frames[r] = (_calc_tilt(x, y, z, rho, rot, self._mask) *
                                    self._transmittance[None, :, :]).astype(
                                        np.uint8)

        self._tilt_transmittance = [None] * 4
        self._tilt_direction = [None] * 4
        self._tilt_retardation = [None] * 4
        for i, data in enumerate(self._tilt_frames):
            self._tilt_transmittance[i], self._tilt_direction[
                i], self._tilt_retardation[i] = _epa(data)

    def clear(self):
        self._angles = np.linspace(0, np.pi, self._n_images, False)
        self._frames = [None] * self._n_images
        self._transmittance = None
        self._direction = None
        self._retardation = None
        self._inclination = None
        self._fom = None
        self._mask = None

        self._tilt_frames = None
        self._tilt_transmittance = None
        self._tilt_direction = None
        self._tilt_retardation = None

    def get(self, x, y):
        x = int(x)
        y = int(y)

        if self.size == 0 or x >= self.frames.shape[
                2] or y >= self.frames.shape[1]:
            return np.array([]), np.array([])

        if self._tilt_mode == 0:
            return self.angles, self.frames[:, y, x]
        if self._tilt_mode > 0:
            return self.angles, self._tilt_frames[self._tilt_mode - 1][:, y, x]
