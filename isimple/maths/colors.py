import abc
import re
from collections import namedtuple
from typing import Dict, Type

import cv2
import numpy as np

# colorspaces
_HSV = 'hsv'
_BGR = 'bgr'
_RGB = 'rgb'


class Color(object):
    _colorspace: str = ''
    _conversion_map: Dict = {}

    def __init__(self, *args, **kwargs):
        # Overloaded by NamedTuple.__init__().
        pass

    def __new__(cls, *args) -> 'Color':
        raise NotImplementedError

    def np(self) -> np.ndarray:
        return np.uint8([[self]])

    def _convert(self, colorspace: str) -> tuple:
        if colorspace not in self._conversion_map:
            raise NotImplementedError
        converted = cv2.cvtColor(self.np(), self._conversion_map[colorspace])
        return tuple(converted.flatten())

    @classmethod
    def from_str(cls, color: str) -> 'Color':
        return cls(
            **{k:int(v.strip("'")) for k,v,_
               in re.findall('([A-Za-z0-9]*)=(.*?)([,)])', color)}
        )


class HsvColor(namedtuple('HsvColor', ('h', 's', 'v')), Color):
    _colorspace: str = _HSV
    _conversion_map = {
        _RGB: cv2.COLOR_HSV2RGB,
        _BGR: cv2.COLOR_HSV2BGR,
    }
    __metaclass__ = Color


class RgbColor(namedtuple('RgbColor', ('r', 'g', 'b')), Color):
    _colorspace: str = _RGB
    _conversion_map = {
        _HSV: cv2.COLOR_RGB2HSV,
        _BGR: cv2.COLOR_RGB2BGR,
    }


class BgrColor(namedtuple('BgrColor', ('b', 'g', 'r')), Color):
    _colorspace: str = _BGR
    _conversion_map = {
        _HSV: cv2.COLOR_BGR2HSV,
        _RGB: cv2.COLOR_BGR2RGB,
    }


# noinspection PyArgumentList
def convert(color: Color, to: Type[Color]) -> Color:
    if type(color) == to:
        return color
    else:
        return to(*color._convert(to._colorspace))
