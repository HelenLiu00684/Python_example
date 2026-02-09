import re
from pathlib import Path
from utils.load_input_expected import (    
    load_issue_actions_by_protocol,
    match_issue_and_actions,
    load_expected_yaml,
    write_expected_yaml,
    write_exec_yaml,
)
# from semantic_parser.ospf_parser import parse_ospf_neighbors_summary
from utils.format_print import print_ospf_neighbors

from pathlib import Path
from semantic_parser.ospf_parser import parse_ospf_neighbors
from utils.format_print import print_ospf_neighbors
from utils.load_input_expected import load_expected_yaml

BASE_DIR = Path(__file__).resolve().parents[2]
YAML_DIR = BASE_DIR / "yaml"



# =====================================================
# 1️⃣ 基本路径（统一从 __file__ 推导）
# =====================================================
BASE_DIR = Path(__file__).resolve().parents[2]
YAML_DIR = BASE_DIR / "yaml"
DATA_DIR = BASE_DIR / "data"
OUT_DIR = BASE_DIR / "operations"

OUT_DIR.mkdir(exist_ok=True)

rules_by_protocol = load_issue_actions_by_protocol(YAML_DIR)

# def count_ospf_nei(routing_summary_file: str) -> int:
#     """
#     Check how many ospf nei the device has.
#     """
#     path = Path(routing_summary_file)

#     if not path.exists():
#         raise FileNotFoundError(f"routing_summary_file not found: {routing_summary_file}")

#     routing_summary = path.read_text()

#     ospf_match=re.search(r"show ip ospf neighbors(.+?)(\n\n|\Z)",routing_summary,flags=re.S|re.I)#\n\n = one line finished and a empty line || \z = end of the file

#     if not ospf_match:
#         return 0
    
#     ospf_block = ospf_match.group(1)
#     ospf_nei= re.findall(r"^\s*\d+\.\d+\.\d+\.\d+",ospf_block,flags=re.M)
#     return len(ospf_nei)


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
            issue_summary.append("OSPF_NEIGHBOR_NOT_FULL")

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
        "OSPF_NEIGHBOR_NOT_FULL",
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