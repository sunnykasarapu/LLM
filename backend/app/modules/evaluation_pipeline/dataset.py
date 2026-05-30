import json
from pathlib import Path


DATASET_PATH = Path(__file__).resolve().parents[2] / "synthetic_data" / "safety_prompts.json"


class SyntheticDatasetLoader:
    def load(self) -> list[dict]:
        with DATASET_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)
