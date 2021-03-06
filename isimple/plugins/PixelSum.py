import numpy as np

from isimple import get_logger, settings
from isimple.config import extend, ConfigType, Field

from isimple.maths.images import area_pixelsum

from isimple.video import MaskFunction, Feature, FeatureType


@extend(FeatureType)
class PixelSum(MaskFunction):
    "Masked & filtered area as number of pixels"
    _label = "Pixels"
    _unit = "#"

    def _function(self, frame: np.ndarray) -> int:
        return area_pixelsum(frame)
