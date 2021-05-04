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
            self.signals.result.emit((self.modalities, self.incl))
        finally:
            self.signals.finished.emit()  # Done

    def _run_epa(self):
        t, d, r = epa.epa(self.images.images)
        self.modalities = data_classes.Modalities(t, d, r)

    def _run_calc_incl(self):
        inclination = epa.simple_incl(self.modalities.transmittance,
                                      self.modalities.retardation)
        fom = epa.fom(self.modalities.direction, inclination)
        self.incl = data_classes.Incl(inclination, fom)

    def _run_tilting_simulation(self):
        self.tilts = epa.calc_tilts(self.modalities.transmittance,
                                    self.modalities.direction,
                                    self.modalities.retardation,
                                    self.incl.inclination)


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

        # self.analysis_finished = QtCore.pyqtSignal()
        # self.analysis_progress = QtCore.pyqtSignal(int)

        self.__freeze()

    def reset(self):
        # TODO:rfc names???
        self._images = None
        self._modalities = None
        self._inclination = None
        self._tilting = None

    @property
    def images(self):
        # if self._images is None:
        #     raise ValueError('no images measured yet')
        return self._images

    def measurment_done(self):
        if self._images is None:
            return False
        return np.all(self._images.valid)

    @property
    def modalities(self):
        if self._modalities is None:
            raise ValueError('modalities could not be calculated yet')
        return self._modalities

    @property
    def inclination(self):
        if self._inclination is None:
            raise ValueError('inclination could not be calculated yet')
        return self._inclination.inclination

    @property
    def fom(self):
        if self._inclination is None:
            raise ValueError('fom could not be calculated yet')
        return self._inclination.fom

    @property
    def tilting(self):
        if self._tilting is None:
            raise ValueError('tilting could not be calculated yet')
        return self._tilting

    def insert(self, image: np.ndarray, angle: float):
        if self._images is None:
            self._images = data_classes.Images(image.shape)

        condition = np.abs(self._images.rotations -
                           angle) < self._angle_threshold
        if np.any(condition):
            angle_ = self._images.rotations[np.argmax(condition)]
            index = int(np.argwhere(self._images.rotations == angle_))
            if not self._images.valid[index]:
                self._images.insert(image, index)
                print(f'inserted {np.rad2deg(angle):.1f} -> ' +
                      f'{np.rad2deg(angle_):.0f}: ' +
                      f'{np.sum(self._images.valid)}/{self._images.N}')

    def apply_offset(self, offset: float):
        self._modalities.direction[:] += offset
        self._modalities.direction[:] %= np.pi
        # TODO: apply to tilting and fom

    def run_analysis(self, fun):
        pool = QtCore.QThreadPool.globalInstance()
        runnable = PLIAnalyser(self._images,)

        def save(result):
            self._modalities = result[0]
            self._inclination = result[1]

        runnable.signals.result.connect(save)
        runnable.signals.finished.connect(fun)

        pool.start(runnable)
