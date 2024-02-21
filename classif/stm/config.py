from typing import List, Set

from dataclasses import dataclass
from dataclasses import field


@dataclass(frozen=True)
class Config:
    STM_URL: str = "https://www.portoreports.com/stm"