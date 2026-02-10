# src/ai/ai_analyzer.py

from pathlib import Path
import yaml

from src.ai.issue_loader import load_operation_yamls
from src.ai.correlator import correlate_by_device


def run_ai_analysis(operations_dir: Path, output_path: Path):
    entries = load_operation_yamls(operations_dir)

    print(f"[DEBUG] Loaded {len(entries)} issue YAMLs")

    analysis = correlate_by_device(entries,debug=True)

    with open(output_path, "w") as f:
        yaml.safe_dump(
            {"ai_analysis": analysis},
            f,
            sort_keys=False
        )

    print(f"AI analysis written to {output_path}")
