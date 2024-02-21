from typing import List, Set

from dataclasses import dataclass
from dataclasses import field


@dataclass(frozen=True)
class Config:
    AMINO_ACIDS: str = "XACDEFGHIKLMNPQRSTVWY"
