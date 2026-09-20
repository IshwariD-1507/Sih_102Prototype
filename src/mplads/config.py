from pathlib import Path
import yaml


ROOT_DIR = Path(__file__).resolve().parents[2]


def load_yaml(relative_path: str):
    path = ROOT_DIR / relative_path

    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


CONFIG = load_yaml("configs/config.yaml")
RISK_CONFIG = load_yaml("configs/risk_weights.yaml")


def get_path(name: str) -> Path:
    return ROOT_DIR / CONFIG["paths"][name]
