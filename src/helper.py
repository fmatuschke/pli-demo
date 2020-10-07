import numpy as np
import os
import cv2

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                         "data", "pli-logo.png")

LOGO_IMG = cv2.imread(LOGO_PATH, cv2.IMREAD_COLOR)


def diff_orientation(a, b):

    a = a % np.pi
    a = a + np.pi
    a = a % np.pi

    b = b % np.pi
    b = b + np.pi
    b = b % np.pi

    diff = [
        a - b, (a + np.pi) - b, (a - np.pi) - b, a - (b + np.pi),
        a - (b - np.pi)
    ]
    idx = np.argmin(np.abs(diff))

    return diff[idx]
