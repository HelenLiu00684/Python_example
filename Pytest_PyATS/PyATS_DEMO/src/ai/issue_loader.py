# src/ai/issue_loader.py

from pathlib import Path
import yaml


def load_operation_yamls(operations_dir: Path) -> list[dict]:
    issues = []

    for path in operations_dir.glob("*.yaml"):
        if path.name == "ai_analysis.yaml":
            continue

        with open(path, "r") as f:
            data = yaml.safe_load(f)

        if not data:
            continue

        # delete the outer package
        if isinstance(data, dict) and "operation" in data:
            issues.append(data["operation"])
        else:
            issues.append(data)

    return issues