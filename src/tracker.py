from __future__ import annotations

import typing

import cv2
import numpy as np
import scipy.stats


class Tracker:
    __is_frozen = False

    def __setattr__(self, key, value):
        if self.__is_frozen and not hasattr(self, key):
            raise TypeError('%r is a frozen class' % self)
        object.__setattr__(self, key, value)

    def __freeze(self):
        self.__is_frozen = True

    def __init__(self, num_sticker: int, sticker_zero_id: int):
        """ 
        num_sticker: number of stickers on pli
        sticker_zero_id: cv sticker id of sticker which should indicate rot=0
        """
        self.reset()
        self._num_sticker = num_sticker
        self._sticker_zero_id = sticker_zero_id
        self.__freeze()

    def reset(self):
        self._cal_corners = None
        self._cal_ids = None
        self._cur_corners = None
        self._cur_ids = None
        self._radius = None
        self._mask = None
        self._input_shape = None
        self._illumination_center = None
        self._illumination_radius = None
        self._sticker_zero_angle = None

    def calibrated(self):
        if self._cal_corners is None:
            return False
        return self._cal_corners.shape[0] == self._num_sticker

    def mask(self, image: np.ndarray) -> np.ndarray:
        if not self.calibrated():
            raise ValueError(' tracker not calibrated yet')

        if self._mask is None:
            x = np.arange(0, self._input_shape[0], dtype=np.float64)
            y = np.arange(0, self._input_shape[1], dtype=np.float64)
            X = np.repeat(x[:, None], self._input_shape[1], axis=1)
            Y = np.repeat(y[None, :], self._input_shape[0], axis=0)
            X -= self._illumination_center[1]
            Y -= self._illumination_center[0]
            self._mask = X**2 + Y**2 < self._illumination_radius**2
            self._mask = self.crop(self._mask)

        if image.ndim == 2:
            res = np.multiply(self._mask, image)
        else:
            res = np.multiply(self._mask[:, :, None], image)
        return res

    def _crop_init(self):
        if not self.calibrated():
            raise ValueError(' tracker not calibrated yet')
        x = np.arange(0, self._input_shape[1], dtype=np.float64)
        y = np.arange(0, self._input_shape[0], dtype=np.float64)
        x -= self._illumination_center[0]
        y -= self._illumination_center[1]
        x = np.abs(x)
        y = np.abs(y)

        return x, y

    def crop_offset(self):
        x, y = self._crop_init()
        x_start = int(np.argmax(x < self._illumination_radius))
        y_start = int(np.argmax(y < self._illumination_radius))

        return y_start, x_start

    def crop(self, image: np.ndarray) -> np.ndarray:
        x, y = self._crop_init()
        x_start = int(np.argmax(x < self._illumination_radius))
        x_end = x.size - int(np.argmax(x[::-1] < self._illumination_radius)) - 1
        y_start = int(np.argmax(y < self._illumination_radius))
        y_end = y.size - int(np.argmax(y[::-1] < self._illumination_radius)) - 1

        return np.ascontiguousarray(image[y_start:y_end, x_start:x_end])

    def current_angle(self, image: np.ndarray) -> typing.Optional[float]:
        cv_corners, cv_ids = self._process_image(image)

        corners = np.array(cv_corners)
        corners.shape = (-1, 4, 2)
        ids = np.array(cv_ids).ravel()

        if ids[0] is None:
            return None

        phi = []
        for j in range(ids.size):
            center_sticker = np.mean(corners[j, :, :], axis=0)

            # calc ref vector and current sticker vector
            i = np.argwhere(np.array(self._cal_ids) == ids[j])
            ref = np.mean(np.squeeze(self._cal_corners[i, :, :]),
                          axis=0) - self._illumination_center
            cur = center_sticker - self._illumination_center

            # calc angle
            z = cur[0] * ref[1] - cur[1] * ref[0]  # helper for 2d sign problem
            value = np.dot(ref,
                           cur) / (np.linalg.norm(ref) * np.linalg.norm(cur))
            value = max(-1.0, min(1.0, value))
            phi.append(np.arccos(value) * np.sign(z))
        return scipy.stats.circmean(
            np.array(phi) - self._sticker_zero_angle, np.pi, 0)

    def _filter_image(self, image: np.ndarray) -> np.ndarray:
        """ filter image to improve tracking """
        image = cv2.medianBlur(image, 3)
        image = (255 - image)  # inverted codes
        return image

    def _process_image(self,
                       image: np.ndarray) -> tuple[typing.Any, typing.Any]:
        image = self._filter_image(image)
        cv2.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
        parameters = cv2.aruco.DetectorParameters_create()
        cv_corners, cv_ids, _ = cv2.aruco.detectMarkers(image,
                                                        cv2.aruco_dict,
                                                        parameters=parameters)

        self._cur_corners = np.array(cv_corners)
        self._cur_ids = np.array(cv_ids)

        return cv_corners, cv_ids

    def add_info_view(self, image):
        image = self._filter_image(image)
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        cv2.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
        parameters = cv2.aruco.DetectorParameters_create()
        cv_corners, cv_ids, _ = cv2.aruco.detectMarkers(image,
                                                        cv2.aruco_dict,
                                                        parameters=parameters)
        if len(cv_corners) > 0:
            image = cv2.aruco.drawDetectedMarkers(image, cv_corners, cv_ids)
            image = image

        if self._illumination_center is not None:
            # center
            image = cv2.circle(
                image,
                (self._illumination_center[0], self._illumination_center[1]), 4,
                (0, 255, 255), 4)
            # center view
            image = cv2.circle(
                image,
                (self._illumination_center[0], self._illumination_center[1]),
                int(self._illumination_radius), (0, 255, 255), 4)

        return image

    def calibrate(self, image: np.ndarray) -> bool:

        self.reset()

        # find all sticker ids
        cv_corners, cv_ids = self._process_image(image)
        if len(cv_corners) != self._num_sticker:
            # did not find all stickers
            return False

        self._input_shape = image.shape

        # all stickers found -> save position of stickers
        self._cal_ids = np.array(cv_ids).ravel()
        self._cal_corners = np.array(cv_corners)
        self._cal_corners.shape = (-1, 4, 2)

        # calc center of pli
        corners = self._cal_corners.copy()
        corners.shape = (-1, 2)
        self._illumination_center = np.mean(corners, axis=0)

        # calc radius of illuminated pli:
        self._illumination_radius = self._calc_illumination_circle_radius()

        # calculate sticker_zero angle
        index_zero_sticker = np.argwhere(
            np.array(self._cal_ids) == self._sticker_zero_id)
        center_zero_sticker = np.mean(np.squeeze(
            self._cal_corners[index_zero_sticker, :, :]),
                                      axis=0)
        ref = np.array((1, 0))  # reference vector in x direction
        cur = center_zero_sticker - self._illumination_center  # vector of sticker
        z = cur[0] * ref[1] - cur[1] * ref[0]  # helper for 2d sign problem
        value = np.dot(ref, cur) / (np.linalg.norm(ref) * np.linalg.norm(cur))
        value = max(-1.0, min(1.0, value))
        self._sticker_zero_angle = (np.arccos(value) * np.sign(z))

        print(f'is calibrated: sticker id {self._sticker_zero_id}' +
              f'-> {np.rad2deg(self._sticker_zero_angle):.2f} deg')

        return True

    def _calc_illumination_circle_radius(self) -> float:
        corners = self._cal_corners.copy()
        corners.shape = (-1, 2)
        return float(
            np.mean(np.linalg.norm(corners - self._illumination_center, axis=1),
                    axis=0)) * 0.75
