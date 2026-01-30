from pathlib import Path

#from routing_summary_parser import status_evpn_nei,parse_ospf_neighbors_summary,parse_bgp_underlay_summary
from utils.routing_summary_parser import (
    status_evpn_nei,
    parse_ospf_neighbors_summary,
    parse_bgp_underlay_summary,
)

# from load_input_expected import (
from utils.load_input_expected import (    
    load_issue_actions_by_protocol,
    match_issue_and_actions,
    load_expected_yaml,
    write_expected_yaml,
    write_exec_yaml,
)

# =====================================================
# 1️⃣ 基本路径（统一从 __file__ 推导）
# =====================================================
BASE_DIR = Path(__file__).resolve().parents[2]
YAML_DIR = BASE_DIR / "yaml"
DATA_DIR = BASE_DIR / "data"
OUT_DIR = BASE_DIR / "operations"

OUT_DIR.mkdir(exist_ok=True)


# =====================================================
# 3️⃣ 加载 rule engine（一次）
# =====================================================
rules_by_protocol = load_issue_actions_by_protocol(YAML_DIR)
# =====================================================
# 4️⃣ 单设备 EVPN 检查函数
# =====================================================

def check_spine_leaf_evpn(
    device_name: str,
    routing_summary_file: Path,
):
    print(f"\n==== Checking EVPN on {device_name} ====")

    evpn_nei_status = status_evpn_nei(str(routing_summary_file))
    print(f"[{device_name}] EVPN neighbor status:", evpn_nei_status)

    evpn_issues = {}

    # 1️⃣ 识别问题
    for peer, info in evpn_nei_status.items():
        if info.get("up_down") != "up":
            evpn_issues[peer] = "EVPN_NEIGHBOR_DOWN"

    # 2️⃣ 无问题：必须 return 统一结构（不是 None）
    if not evpn_issues:
        return {
            "has_issue": False,
            "protocol": "EVPN",
            "issue_summary": [],
            "issue_detail": None,
            "affected_peers": [],
            "actions": [],
        }

    # 3️⃣ 有问题：构造 summary / affected_peers
    issue_summary = list(set(evpn_issues.values()))
    affected_peers = list(evpn_issues.keys())

    # 4️⃣ 从 YAML 里取 action 模板
    action_cfg = load_expected_yaml(
        YAML_DIR / "issue_actions_evpn.yaml",
        "EVPN_NEIGHBOR_DOWN",
    )

    actions = []
    for peer in affected_peers:
        for act in action_cfg.get("actions", []):
            actions.append(act.format(peer=peer))

    # 5️⃣ 返回统一结果（不写 YAML）
    return {
        "has_issue": True,
        "protocol": "EVPN",
        "issue_summary": issue_summary,
        "issue_detail": {
            "neighbors": evpn_nei_status,
        },
        "affected_peers": affected_peers,
        "actions": actions,
    }


def check_single_node_bgp_underlay(
    device_name: str,
    routing_summary_file: Path,
):
    print(f"\n==== Checking BGP underlay on {device_name} ====")

    bgp_summary = parse_bgp_underlay_summary(str(routing_summary_file))

    has_issue = False
    issue_detail = {}
    affected_peers = []
    issue_summary = []
    actions = []

    for peer, info in bgp_summary.items():
        state = info.get("state")

        if state != "Established":
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

    # 读取 action 模板
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



def check_single_node_ospf_underlay(
    device_name: str,
    routing_summary_file: Path,
):
    print(f"\n==== Checking OSPF on {device_name} ====")

    ospf_neighbors = parse_ospf_neighbors_summary(str(routing_summary_file))

    has_issue = False
    issue_detail = {}
    affected_peers = []
    issue_summary = []
    actions = []

    for nbr, info in ospf_neighbors.items():
        raw_state = info.get("raw_state", "")

        # 只要不是 FULL 开头，一律认为异常
        if not raw_state.startswith("FULL"):
            has_issue = True
            issue_detail[nbr] = "OSPF_NEIGHBOR_NOT_FULL"
            affected_peers.append(nbr)
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

    for nbr in affected_peers:
        for act in action_cfg.get("actions", []):
            actions.append(act.format(neighbor=nbr))

    return {
        "has_issue": True,
        "protocol": "OSPF",
        "issue_summary": list(set(issue_summary)),
        "issue_detail": issue_detail,
        "affected_peers": affected_peers,
        "actions": actions,
    }

