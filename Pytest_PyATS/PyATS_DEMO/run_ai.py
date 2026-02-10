# run_ai.py

from pathlib import Path
from src.ai.ai_analyzer import run_ai_analysis
from src.ai.issue_loader import load_operation_yamls

BASE_DIR = Path(__file__).resolve().parent
OPERATIONS_DIR = BASE_DIR / "operations"

if __name__ == "__main__":
    # debug: confirm directory
    print("[DEBUG] OPERATIONS_DIR:", OPERATIONS_DIR)
    print("[DEBUG] exists:", OPERATIONS_DIR.exists())
    print("[DEBUG] files:", list(OPERATIONS_DIR.glob("*")))

    issues = load_operation_yamls(OPERATIONS_DIR)
    print(f"[DEBUG] Loaded {len(issues)} issue YAMLs")

    run_ai_analysis(
        operations_dir=OPERATIONS_DIR,
        output_path=OPERATIONS_DIR / "ai_analysis.yaml"
    )
