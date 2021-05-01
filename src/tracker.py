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
        self._sticker_pos = []
        self._cal_corners = None
        self._cal_ids = None
        self._tracker_view = None
        self._radius = None
        self._illumination_center = None
        self._illumination_radius = None
        self._sticker_zero_angle = None

    def calibrated(self):
        return len(self._sticker_pos) == self._num_sticker

    def current_angle(self, image: np.ndarray) -> typing.Optinal[float, None]:
        cv_corners, cv_ids = self._process_image(image)

        corners = np.array(cv_corners)
        corners.shape = (-1, 4, 2)
        ids = np.array(cv_ids).ravel()

        if ids[0] is None:
            return None

        phi = []
        for j in range(ids.size):
            center_sticker = np.mean(corners[j, :, :], axis=0)
            ref = np.array((1, 0))  # reference vector in x direction
            cur = center_sticker - self._illumination_center  # vector of sticker
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
                       image: np.ndarray) -> tuple(typeing.Any, typeing.Any):
        image = self._filter_image(image)
        cv2.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
        parameters = cv2.aruco.DetectorParameters_create()
        cv_corners, cv_ids, _ = cv2.aruco.detectMarkers(image,
                                                        cv2.aruco_dict,
                                                        parameters=parameters)

        cv_corners_array = np.array(cv_corners)
        cv_ids_array = np.array(cv_ids)
        if cv_corners_array.size > 0:
            image = cv2.aruco.drawDetectedMarkers(image, cv_corners_array,
                                                  cv_ids_array)
            self._tracker_view = image

        if self._illumination_center is not None:
            image = cv2.circle(
                image,
                (self._illumination_center[0], self._illumination_center[1]), 4,
                (0, 255, 0), 4)

            self._tracker_view = cv2.circle(image, (0, 0), 10, (0, 255, 0), 4)

        return cv_corners, cv_ids

    def calibrate(self, image: np.ndarray) -> bool:

        self.reset()

        # find all sticker ids
        cv_corners, cv_ids = self._process_image(image)
        if len(cv_corners) != self._num_sticker:
            # did not find all stickers
            return False

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
        return np.mean(np.linalg.norm(corners - self._illumination_center,
                                      axis=1),
                       axis=0) * 0.75
