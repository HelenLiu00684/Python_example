from pathlib import Path
from semantic_parser.bgp_parser import parse_bgp_neighbors
from utils.format_print import print_bgp_neighbors
from utils.load_input_expected import load_expected_yaml
from utils.load_input_expected import (    
    load_issue_actions_by_protocol,
    load_expected_yaml,
)

import re


BASE_DIR = Path(__file__).resolve().parents[2]
YAML_DIR = BASE_DIR / "yaml"
DATA_DIR = BASE_DIR / "data"
OUT_DIR = BASE_DIR / "operations"

OUT_DIR.mkdir(exist_ok=True)

rules_by_protocol = load_issue_actions_by_protocol(YAML_DIR)

def check_single_node_bgp_underlay(
    device_name: str,
    routing_summary_file: Path,
):
    print(f"\n==== Checking BGP underlay on {device_name} ====")

    bgp_parse = parse_bgp_neighbors(str(routing_summary_file))
    bgp_neighbors = bgp_parse["neighbors"]

    print_bgp_neighbors(device_name, bgp_neighbors)

    has_issue = False
    issue_detail = {}
    affected_peers = []
    issue_summary = []
    actions = []

    for peer, info in bgp_neighbors.items():
        if not info["up"]:
            has_issue = True
            issue_detail[peer] = "BGP_NEIGHBOR_DOWN"#add a label to this issue
            affected_peers.append(peer)
            issue_summary.append("BGP_NEIGHBOR_DOWN")

    if not has_issue:
        return {
            "has_issue": False,
            "protocol": "BGP",
            "issue_summary": [],
            "issue_detail": None,
            "affected_peers": [],
            "actions": [],
        }

    action_cfg = load_expected_yaml(
        YAML_DIR / "issue_actions_bgp.yaml",
        "BGP_NEIGHBOR_DOWN",#open the problem based on the label
    )

    for peer in affected_peers:
        for act in action_cfg.get("actions", []):
            actions.append(act.format(peer=peer))

    return {
        "has_issue": True,
        "protocol": "BGP",
        "issue_summary": list(set(issue_summary)),
        "issue_detail": issue_detail,
        "affected_peers": affected_peers,
        "actions": actions,
    }
