import numpy as np
import cv2

from src import helper


class Stack:

    def __init__(self):
        self.angles = np.linspace(0, np.pi, 9, False)
        self.frames = [None] * 9
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
                self.frames[idx] = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                print(f"inserted {np.rad2deg(self.angles[idx]):.0f}")

    def fit_pixel(self, x, y):
        pass

    def calc_coeffs(self):
        if len(self.frames) == 9:

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
            print("Error, no 9 mesuered images")

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
