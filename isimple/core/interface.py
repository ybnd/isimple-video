import abc
from typing import Type, Tuple, Optional
from dataclasses import dataclass, field

import numpy as np

from pydantic import Field, FilePath, DirectoryPath, Schema

from isimple.core.config import BaseConfig, Instance, Factory, NpArray
from isimple.maths.colors import HsvColor
from isimple.maths.coordinates import Coo


class InterfaceFactory(Factory):
    def get(self) -> Type[Instance]:
        interface = super().get()
        if issubclass(interface, Instance):
            return interface
        else:
            raise TypeError(
                f"'{self.__class__.__name__}' tried to return an unexpected type '{interface}'. "
                f"This is very weird and shouldn't happen, really."
            )


class HandlerConfig(BaseConfig, abc.ABC):
    type: InterfaceFactory
    data: BaseConfig

    def _get_field_type(self, attr):
        """Resolve type of self.data ~ implementation (self.type)
        """
        if attr == 'data':
            return self.type.get().config_class()
        else:
            return super()._get_field_type(attr)


class TransformConfig(BaseConfig):
    """Undefined transform"""
    pass


class TransformInterface(Instance, abc.ABC):
    _config_class: Type[TransformConfig]
    _config: TransformConfig

    @abc.abstractmethod
    def validate(self, matrix: Optional[np.ndarray]) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def from_coordinates(self, roi: dict) -> np.ndarray:
        raise NotImplementedError

    @abc.abstractmethod
    def to_coordinates(self, shape: tuple) -> np.ndarray:
        raise NotImplementedError

    @abc.abstractmethod
    def estimate(self, roi: dict, shape: tuple) -> np.ndarray:
        raise NotImplementedError

    @abc.abstractmethod
    def transform(self, transform, img: np.ndarray, shape: Tuple[int, int]) -> np.ndarray:
        raise NotImplementedError

    @abc.abstractmethod
    def coordinate(self, transform, coordinate: Coo, shape: Tuple[int, int]) -> Coo:
        raise NotImplementedError


class FilterConfig(BaseConfig):
    """Undefined filter"""

    @property
    def ready(self):
        """Return true if filter can be applied ~ this configuration.
            Override for specific filter implementations
        """
        return False


class FilterInterface(Instance, abc.ABC):
    """Handles pixel filtering operations
    """
    _config_class: Type[FilterConfig]

    @abc.abstractmethod
    def set_filter(self, filter, color: HsvColor):
        raise NotImplementedError

    @abc.abstractmethod
    def mean_color(self, filter) -> HsvColor:
        raise NotImplementedError

    @abc.abstractmethod
    def filter(self, filter, image: np.ndarray) -> np.ndarray:
        raise NotImplementedError


class FilterType(InterfaceFactory):
    _type = FilterInterface

    def get(self) -> Type[FilterInterface]:
        filter = super().get()
        if issubclass(filter, FilterInterface):
            return filter
        else:
            raise TypeError(
                f"'{self.__class__.__name__}' tried to return an unexpected type '{filter}'. "
                f"This is very weird and shouldn't happen, really."
            )


class TransformType(InterfaceFactory):
    _type = TransformInterface
