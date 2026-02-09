from pathlib import Path
# from semantic_parser.bgp_parser import parse_bgp_underlay_summary
import re

from utils.load_input_expected import (    
    load_issue_actions_by_protocol,
    match_issue_and_actions,
    load_expected_yaml,
    write_expected_yaml,
    write_exec_yaml,
)
from utils.format_print import print_bgp_neighbors


# =====================================================
# 1️⃣ 基本路径（统一从 __file__ 推导）
# =====================================================
BASE_DIR = Path(__file__).resolve().parents[2]
YAML_DIR = BASE_DIR / "yaml"
DATA_DIR = BASE_DIR / "data"
OUT_DIR = BASE_DIR / "operations"

OUT_DIR.mkdir(exist_ok=True)

rules_by_protocol = load_issue_actions_by_protocol(YAML_DIR)

# def count_bgp_nei(routing_summary_file: str) -> int:
#     """
#     Count how many bpg nei existing in the "show ip ospf nei" including the status are unstable. (Est,Down)
#     """
#     path = Path(routing_summary_file)

#     if not path.exists():
#         raise FileNotFoundError(f"routing_summary_file not found: {routing_summary_file}")

#     routing_summary = path.read_text()

#     bgp_match=re.search(r"show bgp summary([\s\S]+?)(?=\n\S+#|\Z)",routing_summary,flags=re.S|re.I)#\n\n = one line finished and a empty line || \z = end of the file

#     if not bgp_match:
#         return 0
    
#     bgp_block = bgp_match.group(1)

#     bgp_nei= re.findall(r"^\s*\d+\.\d+\.\d+\.\d+",bgp_block,flags=re.M)

#     return len(bgp_nei)


from pathlib import Path
from semantic_parser.bgp_parser import parse_bgp_neighbors
from utils.format_print import print_bgp_neighbors
from utils.load_input_expected import load_expected_yaml

BASE_DIR = Path(__file__).resolve().parents[2]
YAML_DIR = BASE_DIR / "yaml"


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
            issue_detail[peer] = "BGP_NEIGHBOR_DOWN"
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
        "BGP_NEIGHBOR_DOWN",
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
