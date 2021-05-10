from __future__ import annotations

import enum
import functools
import itertools
import os
import pathlib

import numpy as np
import PIL.Image
from PyQt5 import QtCore, QtGui, QtWidgets

from . import capture_device, pli, tracker

# from functools import wraps
# from time import time

# def timing(f):

#     @wraps(f)
#     def wrap(*args, **kw):
#         ts = time()
#         result = f(*args, **kw)
#         te = time()
#         print(f'func:{f.__name__} took: {te - ts:.2f}sec')
#         return result

#     return wrap


def diff_angles(a, b, U):
    d = b - a
    d = (d + U / 2) % U - U / 2
    return d


class MainThread():

    @enum.unique
    class State(enum.Enum):
        TRACKING = enum.auto()
        MEASUREMENT = enum.auto()
        LIVE = enum.auto()

    @enum.unique
    class Tilt(enum.Enum):
        CENTER = 'center'
        NORTH = 'north'
        EAST = 'east'
        SOUTH = 'south'
        WEST = 'west'

    __is_frozen = False

    def __setattr__(self, key, value):
        if self.__is_frozen and not hasattr(self, key):
            raise TypeError('%r is a frozen class' % self)
        object.__setattr__(self, key, value)

    def __freeze(self):
        self.__is_frozen = True

    def __init__(self, parent):
        self.parent = parent
        self.display = self.parent.main_display
        self.reset(msg=False)

        # freeze class
        self.__freeze()

    def reset(self, msg=True):

        if msg:
            print('resetting worker ...')

        self.input_mode = None
        self.state = self.State.TRACKING
        self._debug = False
        self._tilt = self.Tilt.CENTER
        self._xy_buffer = []
        self._last_image = None
        self._image_height = None
        self._image_width = None
        self._last_img_name = 'live'  # same as menue pli actions
        self._angle = None
        self._last_angle = None
        self._update_angle = np.deg2rad(2.5)
        self.parent.plotwidget.clear()

        # pli
        self.pli = pli.PLI(np.deg2rad(self.parent.args.insert_threshold))
        self.parent.main_menu['pli'].set_enabled(False)

        # tracker
        self.tracker = tracker.Tracker(num_sticker=10, sticker_zero_id=10)

        # camera
        self.parent.main_menu['camera']['port'].clear()
        self.device = capture_device.CapDev(port=self.parent.args.port,
                                            file_name=self.parent.args.video)

        for port in self.device.ports():
            self.parent.main_menu['camera']['port'].add_action(
                f'{port}', triggered=functools.partial(self.switch_port, port))

        self.parent.main_menu['camera']['demo'].clear()
        for video in self.device.videos():
            self.parent.main_menu['camera']['demo'].add_action(
                f'{video}',
                triggered=functools.partial(self.switch_video, video))

    def switch_debug(self):
        self._debug = not self._debug

    def to_live_mode(self):
        self.parent.worker.start(self.parent._mspf)
        if not self.tracker.calibrated():
            self.state = self.State.TRACKING
        elif not self.pli.measurment_done():
            self.state = self.State.MEASUREMENT
        else:
            self.state = self.State.LIVE

    def switch_port(self, port):
        self.state = self.State.TRACKING
        self.pli.reset()
        self.tracker.reset()
        self.device.activate_camera(port)

    def check_device_properties(self):
        res = self.device.get_resolutions()
        if res is None:
            print('No device set yet')
            return

        self.parent.main_menu['camera']['resolution'].clear()
        self.parent.main_menu['camera']['resolution'].add_action(
            'scan', lambda: self.check_device_properties())
        for r in res:
            self.parent.main_menu['camera']['resolution'].add_action(
                f'{r[0]}x{r[1]}, {r[2]} fps',
                triggered=functools.partial(self.device.set_prop, r[0], r[1],
                                            r[2]))

    def switch_video(self, video):
        self.state = self.State.TRACKING
        self.pli.reset()
        self.tracker.reset()
        self.device.activate_video(video)

    def convertArray2QImage(self, frame):
        frame = np.ascontiguousarray(frame)
        bytesPerLine = int(frame.nbytes / frame.shape[0])
        if frame.ndim == 2:
            img_format = QtGui.QImage.Format_Grayscale8
        else:
            img_format = QtGui.QImage.Format_RGB888

        qimage = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0],
                              bytesPerLine, img_format)
        qimage = qimage.scaled(self.display.size().width(),
                               self.display.size().height(),
                               QtCore.Qt.KeepAspectRatio,
                               QtCore.Qt.SmoothTransformation)

        return qimage

    def set_tilt(self, tilt):
        self._tilt = self.Tilt(tilt)

    def next(self):
        """ process next iteration """

        valid, frame = self.device.get_frame()

        if not valid:
            print('Error, device disconnected')
            print('---> resetting ...')
            self.reset()

        if self.state == self.State.LIVE:
            self.next_live(frame)
        elif self.state == self.State.TRACKING:
            self.next_tracking(frame)
        elif self.state == self.State.MEASUREMENT:
            self.next_measurement(frame)
        elif self.state in self.State:
            raise ValueError('Not implemented yet')
        else:
            raise ValueError('Undefined State')

        if self._angle is not None:
            self.parent.status_angle.setText(f'{np.rad2deg(self._angle):.1f}')

        if self._debug:
            frame = self.tracker.add_info_view(frame)

        if not self._debug:
            if self.tracker.calibrated():
                frame = self.tracker.crop_img(frame)
                frame = self.tracker.mask_img(frame)
        self.show_image(frame)

        # update plot and gui if rotation is significant
        if self._last_angle is None:
            self._last_angle = self._angle
        else:
            if abs(diff_angles(self._last_angle, self._angle,
                               np.pi)) > self._update_angle:
                self._last_angle = self._angle
                self.update_plot()
                self.update_gui()

    def update_plot(self):
        if len(self._xy_buffer) > 0:
            x_data = self.pli.rotations[self.pli.valid()]
            y_data = []
            for x, y in self._xy_buffer:
                y_data.append(
                    self.pli.images(self._tilt.value)[y, x,
                                                      self.pli.valid()])
            self.parent.plotwidget.update_data(x_data, y_data)
            self.parent.plotwidget.update_rho(self._angle)

    def update_gui(self):
        self.parent.setupwidget.set_rotation(self._angle)
        self.parent.setupwidget.update()

    def update_plot_coordinates_buffer(self,
                                       rel_x_frame_pos,
                                       rel_y_frame_pos,
                                       append=False):

        if self.pli._images is None:
            return

        # to frame coordinates
        x = int(rel_x_frame_pos * self._image_width + 0.5)
        y = int(rel_y_frame_pos * self._image_height + 0.5)

        self.parent.statusbar.showMessage(f'x: {x}, y: {y}', 3000)
        if self._debug:  # better: if cropping is not active
            y_, x_ = self.tracker.crop_offset()
            x -= x_
            y -= y_

        if append:
            self._xy_buffer.append((x, y))
        else:
            self._xy_buffer = [(x, y)]

        print(self._xy_buffer)

        # update plot and draw click indicator
        self.update_plot()
        self.show_image(self._last_image)

    def next_live(self, frame: np.ndarray):
        self._angle = self.tracker.current_angle(frame)

    def enable_pli_results(self):
        self.parent.main_menu['pli'].set_enabled(True)

    def next_measurement(self, frame: np.ndarray):
        if self.pli.measurment_done():
            raise ValueError('measurment already done')

        self._angle = self.tracker.current_angle(frame)
        if self._angle is None:
            raise ValueError('angel is None')

        frame = self.tracker.crop_img(frame)
        frame = self.tracker.mask_img(frame)
        self.pli.insert(frame, self._angle)

        if self.pli.measurment_done():
            self.state = self.State.LIVE
            self.pli.run_analysis(self.enable_pli_results)

    def next_tracking(self, frame: np.ndarray):
        self.show_image(frame)
        if self.tracker.calibrate(frame):
            self.state = self.State.MEASUREMENT

    def _overlay_display(self, pixmap):

        if not self.tracker.calibrated():
            return

        radius = self.tracker._illumination_radius * 0.99
        center = self.tracker._illumination_center[::-1]
        offset = self.tracker.crop_offset()

        # draw red circle
        painter = QtGui.QPainter(pixmap)
        pen = QtGui.QPen()
        scale = pixmap.width() / self._image_width

        pen.setColor(QtCore.Qt.red)
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawEllipse(
            QtCore.QPointF((center[0] - offset[0]) * scale,
                           (center[1] - offset[1]) * scale), radius * scale,
            radius * scale)

        pen.setColor(QtCore.Qt.green)
        pen.setWidth(4)
        painter.setPen(pen)

        if self._angle is None:
            return

        # draw first line
        point_0 = QtCore.QPointF(
            (center[0] - offset[0] + np.cos(-self._angle) * radius * 0.98) *
            scale,
            (center[1] - offset[1] + np.sin(-self._angle) * radius * 0.98) *
            scale)
        point_1 = QtCore.QPointF(
            (center[0] - offset[0] + np.cos(-self._angle) * radius * 1.02) *
            scale,
            (center[1] - offset[1] + np.sin(-self._angle) * radius * 1.02) *
            scale)
        painter.drawLine(point_0, point_1)

        # draw second line
        point_0 = QtCore.QPointF(
            (center[0] - offset[0] +
             np.cos(-self._angle + np.pi) * radius * 0.98) * scale,
            (center[1] - offset[1] +
             np.sin(-self._angle + np.pi) * radius * 0.98) * scale)
        point_1 = QtCore.QPointF(
            (center[0] - offset[0] +
             np.cos(-self._angle + np.pi) * radius * 1.02) * scale,
            (center[1] - offset[1] +
             np.sin(-self._angle + np.pi) * radius * 1.02) * scale)
        painter.drawLine(point_0, point_1)

        # draw green segments
        """
        TODO: draw line is very slow.
        N_points_per_segment > 3 is very slow
        """
        N_points_per_segment = 2 + 1
        for rho in self.pli.rotations[self.pli.valid()]:
            for a, b in zip(
                    np.linspace(-1, 1, N_points_per_segment)[:-1],
                    np.linspace(-1, 1, N_points_per_segment)[1:]):
                point_0 = QtCore.QPointF(
                    (center[0] - offset[0] +
                     np.cos(-rho + np.deg2rad(a * 5)) * radius) * scale,
                    (center[1] - offset[1] +
                     np.sin(-rho + np.deg2rad(a * 5)) * radius) * scale)
                point_1 = QtCore.QPointF(
                    (center[0] - offset[0] +
                     np.cos(-rho + np.deg2rad(b * 5)) * radius) * scale,
                    (center[1] - offset[1] +
                     np.sin(-rho + np.deg2rad(b * 5)) * radius) * scale)
                painter.drawLine(point_0, point_1)

                rho = rho + np.pi
                point_0 = QtCore.QPointF(
                    (center[0] - offset[0] +
                     np.cos(-rho + np.deg2rad(a * 5)) * radius) * scale,
                    (center[1] - offset[1] +
                     np.sin(-rho + np.deg2rad(a * 5)) * radius) * scale)
                point_1 = QtCore.QPointF(
                    (center[0] - offset[0] +
                     np.cos(-rho + np.deg2rad(b * 5)) * radius) * scale,
                    (center[1] - offset[1] +
                     np.sin(-rho + np.deg2rad(b * 5)) * radius) * scale)
                painter.drawLine(point_0, point_1)

        # draw click circles
        # ChartThemeDark Colors (same as plot)
        colors = np.array([(56, 173, 107, 255), (60, 132, 167, 255),
                           (235, 136, 23, 255), (123, 127, 140, 255),
                           (191, 89, 62, 255)], np.uint8)
        for (x, y), c in zip(self._xy_buffer, itertools.cycle(colors)):
            pen.setColor(QtGui.QColor(c[0], c[1], c[2], c[3]))
            painter.setPen(pen)
            painter.drawEllipse(QtCore.QPointF(x * scale, y * scale), 5, 5)

        del painter

    def show_image(self, image):
        self._last_image = image.copy()
        qimage = self.convertArray2QImage(image)
        pixmap = QtGui.QPixmap.fromImage(qimage)
        self._image_height = image.shape[0]
        self._image_width = image.shape[1]

        self._overlay_display(pixmap)
        self.display.setPixmap(pixmap)

    # TODO has nothing to do with worker
    def save_plot(self):
        if len(self._xy_buffer) == 0:
            self.parent.statusbar.showMessage('Plot is empty', 4200)
            return

        self.parent.worker.stop()

        options = QtWidgets.QFileDialog.Options()
        # options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.parent,
            "Save Plot",
            "",
            "Text Files (*.txt);;All Files (*)",
            options=options)

        if file_name:
            if not pathlib.Path(file_name).suffix:
                file_name += '.txt'

            header = ['rho']
            data = [self.pli.rotations[self.pli.valid()]]
            for x, y in self._xy_buffer:
                header.append(f'x{x}y{y}')
                data.append(
                    self.pli.images(self._tilt.value)[y, x,
                                                      self.pli.valid()])
            data = np.vstack(data).T

            delimiter = ','
            header = delimiter.join(header)
            np.savetxt(os.path.join(file_name),
                       data,
                       comments='',
                       fmt='%.6f',
                       delimiter=delimiter,
                       header=header)
        else:
            self.parent.statusbar.showMessage('Invalid file name', 4200)

        self.parent.worker.start(self.parent._mspf)

    # TODO has nothing to do with worker
    def save_images(self):
        if self.pli._inclination is None:
            self.parent.statusbar.showMessage('Images not ready yet', 4200)
            return

        self.parent.worker.stop()

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.AcceptSave

        dialog = QtWidgets.QFileDialog()
        path = dialog.getExistingDirectory(self.parent,
                                           'Save Images',
                                           options=options)

        for file in [
                'rotations.txt', 'stack.tif'
                'transmittance.tif', 'direction.tif', 'retardation.tif',
                'mask.tif', 'inclination.tif', 'fom.tif'
        ]:
            if os.path.isfile(os.path.join(path, file)):
                qm = QtWidgets.QMessageBox
                flag = qm.question(self.parent, '',
                                   "Are you sure to overwrite existing files?",
                                   qm.Yes | qm.No)
                if flag == qm.No:
                    self.save_images()
                    return
                break

        if path:
            np.savetxt(os.path.join(path, 'rotations.txt'), self.pli.rotations)
            stack = []
            data = np.moveaxis(self.pli.images(self._tilt.value), -1, 0)
            for img in data:
                stack.append(PIL.Image.fromarray(img))
            stack[0].save(os.path.join(path, 'stack.tif'),
                          save_all=True,
                          append_images=stack[1:])
            img = PIL.Image.fromarray(self.pli.transmittance())
            img.save(os.path.join(path, 'transmittance.tif'))
            img = PIL.Image.fromarray(self.pli.direction())
            img.save(os.path.join(path, 'direction.tif'))
            img = PIL.Image.fromarray(self.pli.retardation())
            img.save(os.path.join(path, 'retardation.tif'))
            img = PIL.Image.fromarray(self.pli.wm_mask())
            img.save(os.path.join(path, 'wm_mask.tif'))
            img = PIL.Image.fromarray(self.pli.inclination())
            img.save(os.path.join(path, 'inclination.tif'))
            fom = self.pli.fom() * 255
            img = PIL.Image.fromarray(fom.astype(np.uint8))
            img.save(os.path.join(path, 'fom.tif'))

        else:
            self.parent.statusbar.showMessage('Invalid path', 4200)

        self.parent.worker.start(self.parent._mspf)

    # TODO has nothing to do with worker
    def apply_offset(self):
        offset, ok = QtWidgets.QInputDialog.getDouble(self.parent,
                                                      "Offset Value",
                                                      "new offset value")
        if ok:
            offset = np.deg2rad(offset)
            self.pli.apply_offset(offset)
            self.parent.main_menu['pli'][self._last_img_name].trigger()
