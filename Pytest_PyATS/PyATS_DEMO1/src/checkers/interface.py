from pathlib import Path
from semantic_parser.interface_parser import parse_interfaces
from utils.load_input_expected import load_expected_yaml

BASE_DIR = Path(__file__).resolve().parents[2]
YAML_DIR = BASE_DIR / "yaml"


def check_interfaces(
    device_name: str,
    log_file: Path,
):
    """
    Interface checker.

    This checker evaluates interface semantic facts and reports
    interface-level issues.

    Design principles:
    - Interface is treated as a resource layer, not a protocol
    - Only explicit DOWN state generates an issue
    - No counters, flap detection, or historical analysis
    """
    print(f"\n==== Checking INTERFACE on {device_name} ====")

    parsed = parse_interfaces(str(log_file))
    interfaces = parsed["interfaces"]

    issues = {}
    affected = []

    # Rule:
    # Any interface that is not up is considered an issue.
    for intf, info in interfaces.items():
        if not info["up"]:
            issues[intf] = "INTERFACE_DOWN"
            affected.append(intf)

    if not issues:
        return {
            "has_issue": False,
            "protocol": "INTERFACE",
            "issue_summary": [],
            "issue_detail": None,
            "affected_interfaces": [],
            "actions": [],
        }

    # Load remediation actions from YAML definition
    action_cfg = load_expected_yaml(
        YAML_DIR / "issue_actions_interface.yaml",
        "INTERFACE_DOWN",
    )

    actions = []
    for intf in affected:
        for act in action_cfg.get("actions", []):
            actions.append(act.format(interface=intf))

    return {
        "has_issue": True,
        "protocol": "INTERFACE",
        "issue_summary": ["INTERFACE_DOWN"],
        "issue_detail": {
            "interfaces": interfaces,
        },
        "affected_interfaces": affected,
        "actions": actions,
    }
