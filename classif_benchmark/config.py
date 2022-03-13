from dataclasses import dataclass
from dataclasses import field
from typing import List

DBAASP_URL = "https://dbaasp.org/prediction/special/"


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
    AMPSCANNER_MAX_LENGTH: int = 200
