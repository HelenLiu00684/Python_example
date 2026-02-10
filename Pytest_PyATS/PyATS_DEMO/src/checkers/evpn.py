from pathlib import Path
from semantic_parser.evpn_parser import parse_evpn_neighbors
from utils.format_print import print_evpn_neighbors
from utils.load_input_expected import load_expected_yaml

BASE_DIR = Path(__file__).resolve().parents[2]
YAML_DIR = BASE_DIR / "yaml"


def check_evpn_neighbors(
    device_name: str,
    routing_summary_file: Path,
):
    print(f"\n==== Checking EVPN on {device_name} ====")

    evpn_parse = parse_evpn_neighbors(str(routing_summary_file))
    evpn_neighbors = evpn_parse["neighbors"]

    print_evpn_neighbors(device_name, evpn_neighbors)

    evpn_issues = {}

    for peer, info in evpn_neighbors.items():
        if not info["up"]:
            evpn_issues[peer] = "EVPN_NEIGHBOR_DOWN" #add a label to this issue

    if not evpn_issues:
        return {
            "has_issue": False,
            "protocol": "EVPN",
            "issue_summary": [],
            "issue_detail": None,
            "affected_peers": [],
            "actions": [],
        }

    issue_summary = list(set(evpn_issues.values()))
    affected_peers = list(evpn_issues.keys())

    action_cfg = load_expected_yaml(
        YAML_DIR / "issue_actions_evpn.yaml",
        "EVPN_NEIGHBOR_DOWN",                       #open the problem based on the label
    )

    actions = []
    for peer in affected_peers:
        for act in action_cfg.get("actions", []):
            actions.append(act.format(peer=peer))

    return {
        "has_issue": True,
        "protocol": "EVPN",
        "issue_summary": issue_summary,
        "issue_detail": {
            "neighbors": evpn_neighbors,
        },
        "affected_peers": affected_peers,
        "actions": actions,
    }
