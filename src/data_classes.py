from __future__ import annotations

import dataclasses as dc

import numpy as np
import warnings


@dc.dataclass(frozen=True)
class Images:
    # TODO: RFC, variables are instances and shared for all Images
    shape: tuple
    N: int = 18

    images: np.ndarray = dc.field(init=False)
    rotations: np.ndarray = dc.field(init=False)
    valid: np.ndarray = dc.field(init=False)

    def __post_init__(self):
        # resetting np arrays with __setattr__ because of frozen
        object.__setattr__(self, 'images',
                           np.empty((self.shape[0], self.shape[1], self.N)))
        object.__setattr__(self, 'rotations',
                           np.linspace(0, np.pi, self.N, False))
        object.__setattr__(self, 'valid', np.zeros_like(self.rotations,
                                                        np.bool8))

    def apply_offset(self, offset: float) -> None:
        self.rotations[:] = np.linspace(0, np.pi, self.N, False) + offset

    def insert(self, image: np.ndarray, idx: int) -> None:
        if self.valid[idx]:
            warnings.warn('Already image present')

        self.images[:, :, idx] = image
        self.valid[idx] = True

    @property
    def stack(self):
        return self.rotations[self.valid], self.images[:, :, self.valid]

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
class Incl:
    inclination: np.ndarray
    fom: np.ndarray

    def __post_init__(self):
        if self.inclination.ndim != 2:
            raise ValueError(f'inclination ndim: {self.inclination.ndim}')
        if self.fom.ndim != 3:
            raise ValueError(f'fom ndim: {self.fom.ndim}')
        if self.fom.shape[-1] != 3:
            raise ValueError(f'fom.shape[-1]: {self.fom.shape[-1] }')
        if not np.array_equal(self.inclination.shape, self.fom.shape[:-1]):
            raise ValueError(
                f'inclination shape and fom shape differs: {self.inclination.shape}, {self.fom.shape[:-1]}'
            )


# @dc.dataclass(frozen=True)
# class Tilting:
#     north: np.ndarray
#     south: np.ndarray
#     east: np.ndarray
#     west: np.ndarray

#     def __post_init__(self):
#         shape = np.array(self.north.shape)

#         for field in dc.fields(Modalities):
#             elm = getattr(self, field.name)
#             if not np.array_equal(shape, elm.shape[:2]):
#                 raise ValueError(f'{field.name} shape differs from north')

#         for field in dc.fields(Modalities):
#             elm = getattr(self, field.name)
#             if elm.ndim != 2:
#                 raise ValueError(f'{field.name} ndim: {elm.ndim}')
