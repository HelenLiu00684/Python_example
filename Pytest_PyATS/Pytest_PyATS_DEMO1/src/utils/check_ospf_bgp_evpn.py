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

# =====================================================
# 4️⃣ 单设备 bgp 检查函数
# =====================================================
# def check_single_node_bgp_underlay(
#     device_name: str,
#     routing_summary_file: Path,
#     expected_nodes: dict,
#     rules_by_protocol: dict,
# ):
#     """
#     BGP underlay check (summary-based only)
#     All logic is driven by issue_actions_bgp.yaml
#     """

#     # from routing_summary_parser import parse_bgp_underlay_summary

#     bgp_result = {
#         "bgp_issue": False,
#         "bgp_issues": {},   # peer -> issue_name
#         "actions": [],
#     }

#     # 1️⃣ 从 routing_summary 解析 BGP underlay 状态
#     bgp_neighbors = parse_bgp_underlay_summary(str(routing_summary_file))
#     # 示例结构：
#     # {
#     #   "10.0.0.1": {"state": "Established"},
#     #   "10.0.0.2": {"state": "Idle"},
#     # }

#     expected_count = expected_nodes.get(device_name, {}).get(
#         "bgp_underlay_neighbors"
#     )

#     # 2️⃣ 遍历 BGP neighbor
#     for peer, info in bgp_neighbors.items():

#         facts = {
#             "neighbor_state": info.get("state"),
#             "neighbor_count": len(bgp_neighbors),
#             "expected_neighbor_count": expected_count,
#         }

#         issue_name, actions_tpl = match_issue_and_actions(
#             protocol="bgp",
#             facts=facts,
#             rules_by_protocol=rules_by_protocol,
#         )

#         if issue_name:
#             bgp_result["bgp_issue"] = True
#             bgp_result["bgp_issues"][peer] = issue_name

#             for act in actions_tpl:
#                 bgp_result["actions"].append(act.format(peer=peer))

#     return bgp_result
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

# def check_single_node_ospf_underlay(
#     device_name: str,
#     routing_summary_file: Path,
#     log_summary_file: Path,
#     expected_nodes: dict,
#     rules_by_protocol: dict,
# ):
#     """
#     OSPF underlay checker（leaf / spine 统一）

#     规则（最终版）：
#     1. parser 解析到的所有邻居都会被检查（FULL / EXSTART / DOWN 等）
#     2. 只要邻居 state 不在 expected ospf_states 中 → issue
#     3. 同时支持 log-based OSPF 问题（MTU / AUTH / AREA）
#     4. 不区分 leaf / spine 行为，规则完全一致
#     """



#     print(f"\n==== Checking OSPF on {device_name} ====")

#     result = {
#         "ospf_issue": False,
#         "ospf_issues": {},   # peer -> issue_name
#         "actions": [],
#     }

#     # ---------- 角色仅用于取 expected（不影响判断逻辑） ----------
#     role = "leaf" if device_name.startswith("leaf") else "spine"

#     expected_ospf = expected_nodes.get(role, {}).get("ospf", {})
#     expected_states = [s.upper() for s in expected_ospf.get("ospf_states", [])]

#     # ---------- 解析数据 ----------
#     neighbors = parse_ospf_neighbors_summary(str(routing_summary_file))
#     log_text = log_summary_file.read_text() if log_summary_file.exists() else ""

#     # ==================================================
#     # 1️⃣ 邻居状态检查（核心：统一 leaf / spine）
#     # ==================================================
#     for peer, info in neighbors.items():
#         state = info.get("state", "").upper()
#         interface = info.get("interface", "")

#         # FULL 是唯一健康态，其它一律认为 OSPF issue
#         if state not in expected_states:
#             result["ospf_issue"] = True

#             facts = {
#                 "neighbor_state": state,
#                 "log": log_text,
#             }

#             issue_name, actions = match_issue_and_actions(
#                 protocol="ospf",
#                 facts=facts,
#                 rules_by_protocol=rules_by_protocol,
#             )

#             # YAML 没有精确规则时，兜底 issue 名
#             if not issue_name:
#                 issue_name = f"OSPF_NEIGHBOR_STATE_{state}"

#             result["ospf_issues"][peer] = issue_name

#             for act in actions:
#                 result["actions"].append(
#                     act.format(peer=peer, interface=interface)
#                 )

#     # ==================================================
#     # 2️⃣ 日志驱动的 OSPF 问题（与邻居无关）
#     # ==================================================
#     for issue_name, rule in rules_by_protocol.get("ospf", {}).items():
#         match = rule.get("match", {})
#         log_error = match.get("log_error")

#         if not log_error:
#             continue

#         if log_error in log_text:
#             result["ospf_issue"] = True
#             result["ospf_issues"]["_log_"] = issue_name

#             for act in rule.get("actions", []):
#                 result["actions"].append(act)

#     return result


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

