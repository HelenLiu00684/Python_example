# utils/testbed_loader.py
import yaml
from pathlib import Path


def load_devices_from_testbed(testbed_file: str = "testbed.yaml") -> dict:#comment as DICT
    """
    Load testbed YAML and return device inventory as dict
    """
    project_root = Path(__file__).resolve().parents[2]
    path = project_root / testbed_file

    if not path.exists():
        raise FileNotFoundError(f"Testbed file not found: {testbed_file}")

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    return data["devices"]

# if __name__ == "__main__":
#     devices = load_devices_from_testbed()
#     print(devices.keys())
#     print(devices.items())

