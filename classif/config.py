from dataclasses import dataclass
from dataclasses import field

from typing import List


@dataclass(frozen=True)
class Config:
    AMINO_ACIDS: str = "XACDEFGHIKLMNPQRSTVWY"

    DBAASP_STRAINS: List[str] = field(default_factory=lambda: [
        "Escherichia coli ATCC 25922",
        "Pseudomonas aeruginosa ATCC 27853",
        "Klebsiella pneumonia",
        "Staphylococcus aureus ATCC 25923",
        "Human erythrocytes",
        "Bacillus Subtilis",
        "Candida albicans",
        "Saccharomyces cerevisiae",
    ])
    DBAASP_URL: str = "https://dbaasp.org/prediction/special/"
    DBAASP_CHUNK_SIZE: int = 400

    STM_URL: str = "https://www.portoreports.com/stm"

    AMPSCANNER_MAX_LENGTH: int = 200
