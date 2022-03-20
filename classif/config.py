from typing import List, Set

from dataclasses import dataclass
from dataclasses import field


@dataclass(frozen=True)
class Config:
    AMINO_ACIDS: str = "XACDEFGHIKLMNPQRSTVWY"
    AVAILABLE_MODELS: Set[str] = field(default_factory=lambda: {
        "ampgram",
        "amplify",
        "ampscannerv2",
        "dbaasp_species",
        # "iamp",
        "stm",
    })

    CAMPR3_URL = "http://www.camp.bicnirrh.res.in/predict/hii.php"
    DBAASP_URL: str = "https://dbaasp.org/prediction/special/"
    STM_URL: str = "https://www.portoreports.com/stm"

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
    DBAASP_CHUNK_SIZE: int = 400

    AMPSCANNER_MAX_LENGTH: int = 200
