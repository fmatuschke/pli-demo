import cv2
import cv2.aruco
import numpy as np
import scipy.stats


class Tracker:

    def __init__(self, num_sticker=10):
        self.is_calibrated = False
        self.num_sticker = num_sticker
        self.center = None
        self.frame = None
        self.rho = 0
        self.img_mask = None

    def filter_image(self, frame):
        if frame.ndim == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.medianBlur(frame, 3)
        frame = (255 - frame)  # inverted codes
        return frame

    def calibrate(self, frame):

        frame = self.filter_image(frame)
        cv2.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
        parameters = cv2.aruco.DetectorParameters_create()
        self.cv_corners, self.cv_ids, _ = cv2.aruco.detectMarkers(
            frame, cv2.aruco_dict, parameters=parameters)
        self.frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        if len(self.cv_corners) != self.num_sticker:
            return

        # save data for reference
        self.cal_corners = np.array(self.cv_corners)
        self.cal_corners.shape = (-1, 4, 2)
        self.cal_ids = np.array(self.cv_ids)
        self.cal_ids.shape = (-1)

        # calc center of pli
        corners = self.cal_corners.copy()
        corners.shape = (-1, 2)
        self.center = np.mean(corners, axis=0)
        self.is_calibrated = len(self.cv_ids) == self.num_sticker
        self.gen_mask()

        print("is calibrated")

    def track(self, frame):

        if not self.is_calibrated:
            print("Error, not calibrate yet")
            return None

        frame = self.filter_image(frame)
        cv2.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
        parameters = cv2.aruco.DetectorParameters_create()
        self.cv_corners, self.cv_ids, _ = cv2.aruco.detectMarkers(
            frame, cv2.aruco_dict, parameters=parameters)
        self.frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        corners = np.array(self.cv_corners)
        corners.shape = (-1, 4, 2)
        ids = np.array(self.cv_ids)
        ids.shape = (-1)

        if ids[0] is None:
            return None

        phi = []
        for j in range(ids.size):
            center_qr = np.mean(corners[j, :, :], axis=0)

            # calc ref vector
            i = np.argwhere(np.array(self.cal_ids) == ids[j])
            ref = np.mean(np.squeeze(self.cal_corners[i, :, :]),
                          axis=0) - self.center

            # calc current vector
            cur = center_qr - self.center

            # 3rd comp of cross product
            z = cur[0] * ref[1] - cur[1] * ref[0]

            value = np.dot(ref,
                           cur) / (np.linalg.norm(ref) * np.linalg.norm(cur))
            value = max(-1.0, min(1.0, value))
            phi.append(np.arccos(value) * np.sign(z))

        self.rho = scipy.stats.circmean(phi, np.pi, 0)
        return self.rho

    def show(self):
        frame = cv2.aruco.drawDetectedMarkers(self.frame, self.cv_corners,
                                              self.cv_ids)
        if self.center is not None:
            frame = cv2.circle(frame, (self.center[0], self.center[1]), 4,
                               (0, 255, 0), 4)

        return frame

    def gen_mask(self):
        if not self.is_calibrated:
            print("Error, not calibrate yet")
            return None

        Y, X = np.ogrid[:self.frame.shape[0], :self.frame.shape[1]]
        dist2_from_center = (X - self.center[0])**2 + (Y - self.center[1])**2

        self.img_mask = dist2_from_center <= (min(self.frame.shape[:2]) *
                                              0.28)**2
