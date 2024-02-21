from typing import List, Set

from dataclasses import dataclass
from dataclasses import field


@dataclass(frozen=True)
class Config:
    AMPSCANNER_MAX_LENGTH: int = 200
    AMPSCANNER_MIN_LENGTH: int = 10
    AMPSCANNER_THRESHOLD: float = 0.5

    AMPSCANNER_MODEL_PATH: str = "resources/models/ampscannerv2_021820_full_model.h5"
