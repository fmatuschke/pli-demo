import cv2
import cv2.aruco
import numpy as np
import scipy.stats


class Tracker:

    def __init__(self, num_sticker=10):
        self._is_calibrated = False
        self._num_sticker = num_sticker
        self._center = None
        self._radius = 0
        self._frame = None
        self._rho = 0
        self._mask = None

    @property
    def radius(self):
        if not self._is_calibrated:
            print("Warning, not yet calibrated")
        return self._radius

    @property
    def center(self):
        if not self._is_calibrated:
            print("Warning, not yet calibrated")
        return self._center

    @property
    def frame(self):
        return self._frame

    @property
    def rho(self):
        if not self._is_calibrated:
            print("Warning, not yet calibrated")
        return self._rho

    @property
    def mask(self):
        if not self._is_calibrated:
            print("Warning, not yet calibrated")
        return self._mask

    @property
    def is_calibrated(self):
        return self._is_calibrated

    def _filter_image(self, frame):
        if frame.ndim == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.medianBlur(frame, 3)
        frame = (255 - frame)  # inverted codes
        return frame

    def calibrate(self, frame):
        frame = self._filter_image(frame)
        cv2.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
        parameters = cv2.aruco.DetectorParameters_create()
        self._cv_corners, self._cv_ids, _ = cv2.aruco.detectMarkers(
            frame, cv2.aruco_dict, parameters=parameters)
        self._frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        if len(self._cv_corners) != self._num_sticker:
            return

        # SAVE calibration
        self._is_calibrated = True

        # save data for reference
        self._cal_corners = np.array(self._cv_corners)
        self._cal_corners.shape = (-1, 4, 2)
        self._cal_ids = np.array(self._cv_ids)
        self._cal_ids.shape = (-1)

        # calc center of pli
        corners = self._cal_corners.copy()
        corners.shape = (-1, 2)
        self._center = np.mean(corners, axis=0)

        # calc image radius:
        # for c in self._cal_corners:

        self._radius = np.mean(np.linalg.norm(corners - self._center, axis=1),
                               axis=0)
        self._gen_mask()

        print("is calibrated")

    def track(self, frame):

        if not self._is_calibrated:
            print("Warning, not yet calibrated")
            return None

        frame = self._filter_image(frame)
        cv2.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
        parameters = cv2.aruco.DetectorParameters_create()
        self._cv_corners, self._cv_ids, _ = cv2.aruco.detectMarkers(
            frame, cv2.aruco_dict, parameters=parameters)
        self._frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        corners = np.array(self._cv_corners)
        corners.shape = (-1, 4, 2)
        ids = np.array(self._cv_ids)
        ids.shape = (-1)

        if ids[0] is None:
            return None

        phi = []
        for j in range(ids.size):
            center_qr = np.mean(corners[j, :, :], axis=0)

            # calc ref vector
            i = np.argwhere(np.array(self._cal_ids) == ids[j])
            ref = np.mean(np.squeeze(self._cal_corners[i, :, :]),
                          axis=0) - self._center

            # calc current vector
            cur = center_qr - self._center

            # 3rd comp of cross product
            z = cur[0] * ref[1] - cur[1] * ref[0]

            value = np.dot(ref,
                           cur) / (np.linalg.norm(ref) * np.linalg.norm(cur))
            value = max(-1.0, min(1.0, value))
            phi.append(np.arccos(value) * np.sign(z))

        self._rho = scipy.stats.circmean(phi, np.pi, 0)
        return self._rho

    def show(self):
        frame = cv2.aruco.drawDetectedMarkers(self._frame, self._cv_corners,
                                              self._cv_ids)
        if self._center is not None:
            frame = cv2.circle(frame, (self._center[0], self._center[1]), 4,
                               (0, 255, 0), 4)

            frame = cv2.circle(frame, (0, 0), 10, (0, 255, 0), 4)

        return frame

    def _gen_mask(self):
        if not self._is_calibrated:
            print("Warning, not yet calibrated")
            return None

        Y, X = np.ogrid[:self._frame.shape[0], :self._frame.shape[1]]
        dist2_from_center = (X - self._center[0])**2 + (Y - self._center[1])**2

        self._mask = dist2_from_center <= (min(self._frame.shape[:2]) * 0.28)**2
