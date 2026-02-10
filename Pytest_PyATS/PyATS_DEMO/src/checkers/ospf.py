import re
from pathlib import Path
from utils.load_input_expected import (    
    load_issue_actions_by_protocol,
    load_expected_yaml,

)
from utils.format_print import print_ospf_neighbors
from semantic_parser.ospf_parser import parse_ospf_neighbors

BASE_DIR = Path(__file__).resolve().parents[2]
YAML_DIR = BASE_DIR / "yaml"
DATA_DIR = BASE_DIR / "data"
OUT_DIR = BASE_DIR / "operations"

OUT_DIR.mkdir(exist_ok=True)

rules_by_protocol = load_issue_actions_by_protocol(YAML_DIR)


def check_single_node_ospf_underlay(
    device_name: str,
    routing_summary_file: Path,
):
    print(f"\n==== Checking OSPF on {device_name} ====")

    ospf_parse = parse_ospf_neighbors(str(routing_summary_file))
    ospf_neighbors = ospf_parse["neighbors"]

    print_ospf_neighbors(device_name, ospf_neighbors)

    has_issue = False
    issue_detail = {}
    affected_peers = []
    issue_summary = []
    actions = []

    for peer, info in ospf_neighbors.items():
        if not info["up"]:
            has_issue = True
            issue_detail[peer] = "OSPF_NEIGHBOR_NOT_FULL"
            affected_peers.append(peer)
            issue_summary.append("OSPF_NEIGHBOR_NOT_FULL")#add a label to this issue

    if not has_issue:
        return {
            "has_issue": False,
            "protocol": "OSPF",
            "issue_summary": [],
            "issue_detail": None,
            "affected_peers": [],
            "actions": [],
        }

    action_cfg = load_expected_yaml(
        YAML_DIR / "issue_actions_ospf.yaml",
        "OSPF_NEIGHBOR_NOT_FULL",#open the problem based on the label
    )

    for peer in affected_peers:
        for act in action_cfg.get("actions", []):
            actions.append(act.format(neighbor=peer))

    return {
        "has_issue": True,
        "protocol": "OSPF",
        "issue_summary": list(set(issue_summary)),
        "issue_detail": issue_detail,
        "affected_peers": affected_peers,
        "actions": actions,
    }