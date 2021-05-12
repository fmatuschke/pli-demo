from __future__ import annotations

import dataclasses as dc

import numpy as np
import warnings


@dc.dataclass(frozen=True)
class Images:
    # TODO: RFC, variables are instances and shared for all Images
    shape: tuple

    images: np.ndarray = dc.field(init=False)
    rotations: np.ndarray = dc.field(init=False)
    valid: np.ndarray = dc.field(init=False)

    def __post_init__(self):
        # resetting np arrays with __setattr__ because of frozen
        object.__setattr__(self, 'images', np.empty(self.shape))
        object.__setattr__(self, 'rotations',
                           np.linspace(0, np.pi, self.shape[-1], False))
        object.__setattr__(self, 'valid', np.zeros_like(self.rotations,
                                                        np.bool8))

    def insert(self, image: np.ndarray, idx: int) -> None:
        if self.valid[idx]:
            warnings.warn('Already image present')

        self.images[:, :, idx] = image
        self.valid[idx] = True

    def stack(self):
        return self.rotations[self.valid], self.images[:, :, self.valid]


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
    wm_mask: np.ndarray


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
