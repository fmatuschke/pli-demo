import numpy as np
import os
import cv2


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
