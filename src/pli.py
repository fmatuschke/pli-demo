from __future__ import annotations

# import dataclasses
import dataclasses as dc
import typing

import numpy as np

from . import epa


@dc.dataclass(frozen=True)
class Images:
    shape: tuple
    N = 18
    images = np.empty((0, 0, N))
    rotations = np.linspace(0, np.pi, N, False)

    def __post_init__(self,):
        object.__setattr__(self, 'images',
                           np.empty((self.shape[0], self.shape[1], self.N)))

    def apply_offset(self, offset: float) -> None:
        self.rotations[:] = np.linspace(0, np.pi, self.N, False) + offset

    def insert(self, image: np.ndarray, angle: float) -> None:
        if angle not in self.rotations:
            raise ValueError(
                f'angle not in rotations: {angle} not in {self.rotations}')

        self.images[:, :, np.where(self.rotations == angle)] = image

    @property
    def offset(self) -> float:
        return self.rotations[0]


@dc.dataclass(frozen=True)
class Modalities:
    transmittance: np.ndarray
    direction: np.ndarray
    retardation: np.ndarray

    def __post_init__(self):
        shape = np.array(self.transmittance.shape)

        for field in dc.fields(Modalities):
            elm = getattr(self, field.name)
            if not np.array_equal(shape, elm.shape[:2]):
                raise ValueError(
                    f'{field.name} shape differs from transmittance')

        for field in dc.fields(Modalities):
            elm = getattr(self, field.name)
            if elm.ndim != 2:
                raise ValueError(f'{field.name} ndim: {elm.ndim}')


@dc.dataclass(frozen=True)
class Tilting:
    north: np.ndarray
    south: np.ndarray
    east: np.ndarray
    west: np.ndarray

    def __post_init__(self):
        shape = np.array(self.north.shape)

        for field in dc.fields(Modalities):
            elm = getattr(self, field.name)
            if not np.array_equal(shape, elm.shape[:2]):
                raise ValueError(f'{field.name} shape differs from north')

        for field in dc.fields(Modalities):
            elm = getattr(self, field.name)
            if elm.ndim != 2:
                raise ValueError(f'{field.name} ndim: {elm.ndim}')


@dc.dataclass(frozen=True)
class Incl:
    inclination: np.ndarray
    fom: np.ndarray

    def __post_init__(self):
        if inclination.ndim != 2:
            raise ValueError(f'inclination ndim: {inclination.ndim}')
        if fom.ndim != 3:
            raise ValueError(f'fom ndim: {fom.ndim}')
        if fom.shape[-1] != 3:
            raise ValueError(f'fom.shape[-1]: {fom.shape[-1] }')
        if np.array_equal(inclination.shape, fom.shape[:-1]):
            raise ValueError('inclination shape and fom shape differs')


class PLI(object):

    __is_frozen = False

    def __setattr__(self, key, value):
        if self.__is_frozen and not hasattr(self, key):
            raise TypeError('%r is a frozen class' % self)
        object.__setattr__(self, key, value)

    def __freeze(self):
        self.__is_frozen = True

    def __init__(self, threshold):
        self.reset()
        self._angle_threshold = np.deg2rad(threshold)
        self.__freeze()

    def reset(self):
        self._images = None
        self._modalities = None
        self._inclination = None
        self._tilting = None

    @property
    def images(self):
        if self._images is None:
            raise ValueError('no images measured yet')
        return self._images.copy()

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
            self._images = Images(image.shape)

        condition = np.abs(self._images.rotations -
                           angle) < self._angle_threshold
        if np.any(condition):
            self._images.insert(image,
                                self._images.rotations[np.argmax(condition)])

    def apply_offset(self, offset: float):
        self._modalities.direction[:] += offset
        self._modalities.direction[:] %= np.pi
        # TODO: apply to tilting and fom

    def _run_analysis(self):
        self._run_epa()
        self._run_calc_incl()
        self._run_tilting_simulation()

    def _run_tilting_simulation(self):
        pass

    def _run_epa(self):
        t, d, r = epa.epa(self._images.data)
        self._modalities = Modalities(t, d, r)
        self.apply_offset(self._images.offset)

    def _run_calc_incl(self):
        pass
