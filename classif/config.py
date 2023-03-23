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
        "dbaasp_genome",
        "stm",
        "campr3_svm",
        "campr3_rf",
        "campr3_ann",
        "campr3_da",
    })
    TOXICITY_MODELS: Set[str] = field(default_factory=lambda: {
        "dbaasp_species",
        "happnn",
        "hemopred",
        "hlppred_fuse",
    })

    CAMPR3_URL: str = "http://www.camp.bicnirrh.res.in/predict/hii.php"
    DBAASP_GENERAL_URL: str = "https://dbaasp.org/prediction/general"
    DBAASP_STRAIN_URL: str = "https://dbaasp.org/prediction/special/"
    DBAASP_GENOME_URL: str = "https://dbaasp.org/prediction/genome"
    STM_URL: str = "https://www.portoreports.com/stm"
    HAPPNN_URL: str = "https://research.timmons.eu/happenn"

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
    DBAASP_GENOME_STRAINS: List[str] = field(default_factory=lambda: [
        "Escherichia coli ATCC 25922",
        "Pseudomonas aeruginosa ATCC 27853",
        "Klebsiella pneumoniae ATCC 700603",
        "Salmonella typhimurium ATCC 14028",
        "Acinetobacter baumannii ATCC 19606",
        "Staphylococcus aureus ATCC 25923",
        "Enterococcus faecalis ATCC 29212",
        "Bacillus subtilis ATCC 6633",
    ])

    DBAASP_CHUNK_SIZE: int = 150
    DBAASP_GENOME_CHUNK_SIZE: int = 150
    AMPSCANNER_MAX_LENGTH: int = 200
    AMPSCANNER_MIN_LENGTH: int = 10
    AMPSCANNER_THRESHOLD: float = 0.5

    AMPSCANNER_MODEL_PATH: str = "../resources/models/ampscannerv2_021820_full_model.h5"
    CAMPR3_AVAILABLE_MODELS: List[str] = field(default_factory=lambda: [
        "svm",
        "rf",
        "ann",
        "da",
    ])

    MODELS_FOR_CANDIDATE_SELECTION: List[str] = field(default_factory=lambda: [
        "amplify",
        "campr3_rf",
        "stm",
    ])
    GRID_SCALE: float = 0.01
    TOP_K: int = 60
