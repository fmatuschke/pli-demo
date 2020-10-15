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
        return self._transmittance.copy()

    @property
    def direction(self):
        return self._direction.copy()

    @property
    def retardation(self):
        return self._retardation.copy()

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
                self._frames[idx] = frame
                is_inserted = True

        if self.full:
            if self._ui is not None:
                self._ui.statusBar().showMessage(f"analysing")
            print("calc_coeffs")
            self.calc_coeffs()
            print("calc_fom")
            self.calc_fom()

        return is_inserted

    def fit_pixel(self, x, y):
        pass

    def calc_coeffs(self):
        if len(self._frames) == self._n_images:

            data = np.array(self._frames, np.float32)
            n = data.shape[0]

            rho_2 = 2 * np.linspace(0, np.pi, n, False, dtype=data.dtype)

            a0 = np.sum(data, 0) / n
            a1 = 2 * np.sum(data * np.sin(rho_2)[:, None, None], 0) / n
            b1 = 2 * np.sum(data * np.cos(rho_2)[:, None, None], 0) / n

            self._transmittance = 2 * a0
            self._direction = 0.5 * np.arctan2(-b1, a1) + np.pi
            self._retardation = np.sqrt(a1 * a1 + b1 * b1) / (a0 + 1e-16)
        else:
            print(f"Error, no {self._n_images} mesuered images")

    def calc_fom(self):
        self._inclination = self._retardation / np.amax(self._retardation)
        self._fom = fom_hsv_black(self._direction, self._inclination)
        self._mask = self.retardation > 0.05

    def clear(self):
        self._angles = np.linspace(0, np.pi, self._n_images, False)
        self._frames = [None] * self._n_images
        self._transmittance = None
        self._direction = None
        self._retardation = None
        self._inclination = None
        self._fom = None

    def get(self, x, y):
        x = int(x)
        y = int(y)

        if self.size == 0:
            return np.array([]), np.array([])

        return self.angles, self.frames[:, y, x]
