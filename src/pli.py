from __future__ import annotations

import traceback
import sys

import numpy as np
from PyQt5 import QtCore

from . import epa
from . import data_classes


class WorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal(tuple)


class PLIAnalyser(QtCore.QRunnable):

    def __init__(self, images):
        super(PLIAnalyser, self).__init__()
        self.images = images
        self.signals = WorkerSignals()

    @QtCore.pyqtSlot()
    def run(self):
        try:
            print('thread: running analysis ...')
            self._run_epa()
            self._run_calc_incl()
            self._run_tilting_simulation()
            print('thread: analysis finished')
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit((self.modalities, self.incl, self.tilts))
        finally:
            self.signals.finished.emit()  # Done

    def _run_epa(self):
        t, d, r = epa.epa(self.images.images)
        self.modalities = data_classes.Modalities(t, d, r)

    def _run_calc_incl(self):
        inclination, wm_mask = epa.simple_incl(self.modalities.transmittance,
                                               self.modalities.retardation)
        self.incl = data_classes.Incl(inclination, wm_mask)

    def _run_tilting_simulation(self):
        self.tilts = epa.calc_tilts(self.modalities.transmittance,
                                    self.modalities.direction,
                                    self.modalities.retardation,
                                    self.incl.inclination,
                                    self.images.shape[-1])


class PLI():
    __is_frozen = False

    def __setattr__(self, key, value):
        if self.__is_frozen and not hasattr(self, key):
            raise TypeError('%r is a frozen class' % self)
        object.__setattr__(self, key, value)

    def __freeze(self):
        self.__is_frozen = True

    def __init__(self, threshold):
        self.reset()
        self._angle_threshold = threshold
        self._num_rot = 18

        self.__freeze()

    def reset(self):
        # TODO:rfc names???
        self._images = None
        self._modalities = None
        self._inclination = None
        self._tilting = None
        self._fom = None
        self._offset = 0

    def images(self, tilt):
        if tilt == 'center':
            return self._images.images.copy()
        elif tilt == 'north':
            return self._tilting[0][0].copy()
        elif tilt == 'east':
            return self._tilting[0][1].copy()
        elif tilt == 'south':
            return self._tilting[0][2].copy()
        elif tilt == 'west':
            return self._tilting[0][3].copy()
        else:
            raise ValueError(f'wrong tilt: {tilt}')

    def rotations(self):
        rotations = self._images.rotations.copy() + self._offset
        rotations %= np.pi
        rotations += np.pi
        rotations %= np.pi
        return rotations

    def valid(self):
        if self._images is None:
            return None
        return self._images.valid[:]

    def measurment_done(self):
        if self._images is None:
            return False
        return np.all(self._images.valid)

    def transmittance(self, tilt='center'):
        if self._modalities is None:
            print('modalities could not be calculated yet')
            return None

        if tilt == 'center':
            return self._modalities.transmittance.copy()
        elif tilt == 'north':
            return self._tilting[1][0].copy()
        elif tilt == 'east':
            return self._tilting[1][1].copy()
        elif tilt == 'south':
            return self._tilting[1][2].copy()
        elif tilt == 'west':
            return self._tilting[1][3].copy()
        else:
            raise ValueError(f'wrong tilt: {tilt}')

    def direction(self, tilt='center'):
        if self._modalities is None:
            print('modalities could not be calculated yet')
            return None

        if tilt == 'center':
            direction = self._modalities.direction.copy()
        elif tilt == 'north':
            direction = self._tilting[2][0].copy()
        elif tilt == 'east':
            direction = self._tilting[2][1].copy()
        elif tilt == 'south':
            direction = self._tilting[2][2].copy()
        elif tilt == 'west':
            direction = self._tilting[2][3].copy()
        else:
            raise ValueError(f'wrong tilt: {tilt}')

        direction[:] += self._offset
        direction[:] %= np.pi
        direction[:] += np.pi
        direction[:] %= np.pi
        return direction

    def retardation(self, tilt='center'):
        if self._modalities is None:
            print('modalities could not be calculated yet')
            return None

        if tilt == 'center':
            return self._modalities.retardation.copy()
        elif tilt == 'north':
            return self._tilting[3][0].copy()
        elif tilt == 'east':
            return self._tilting[3][1].copy()
        elif tilt == 'south':
            return self._tilting[3][2].copy()
        elif tilt == 'west':
            return self._tilting[3][3].copy()
        else:
            raise ValueError(f'wrong tilt: {tilt}')

    def inclination(self, tilt='center'):
        if self._inclination is None:
            print('inclination could not be calculated yet')
            return None

        if tilt == 'center':
            return self._inclination.inclination.copy()
        elif tilt == 'north':
            return self._tilting[4][0].copy()
        elif tilt == 'east':
            return self._tilting[4][1].copy()
        elif tilt == 'south':
            return self._tilting[4][2].copy()
        elif tilt == 'west':
            return self._tilting[4][3].copy()
        else:
            raise ValueError(f'wrong tilt: {tilt}')

    def wm_mask(self):
        if self._inclination is None:
            print('wm mask could not be calculated yet')
            return None
        return self._inclination.wm_mask.copy()

    def fom(self):
        if self._fom is None:
            if self._inclination is None:
                print('fom could not be calculated yet')
                return None
            self._fom = epa.fom(self.direction(), self.inclination())
        return self._fom.copy()

    def insert(self, image: np.ndarray, angle: float):
        if self._images is None:
            self._images = data_classes.Images(
                list(image.shape) + [self._num_rot])

        condition = np.abs(self._images.rotations -
                           angle) < self._angle_threshold
        if np.any(condition):
            angle_ = self._images.rotations[np.argmax(condition)]
            index = int(np.argwhere(self._images.rotations == angle_))
            if not self._images.valid[index]:
                self._images.insert(image, index)
                print(f'inserted {np.rad2deg(angle):.1f} -> ' +
                      f'{np.rad2deg(angle_):.0f}: ' +
                      f'{np.sum(self._images.valid)}/{self._images.shape[-1]}')

    def apply_offset(self, offset: float):
        self._offset = offset
        if self._fom is not None:
            self._fom[:] = epa.fom(self.direction(), self.inclination())

    def offset(self):
        return self._offset

    def run_analysis(self, fun):
        pool = QtCore.QThreadPool.globalInstance()
        runnable = PLIAnalyser(self._images)

        def save(result):
            self._modalities = result[0]
            self._inclination = result[1]
            self._tilting = result[2]

        runnable.signals.result.connect(save)
        runnable.signals.finished.connect(fun)

        pool.start(runnable)
