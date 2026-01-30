from pathlib import Path
from utils.format_print import print_evpn_neighbors
from semantic_parser.evpn_parser import parse_evpn_neighbors

#from semantic_parser import parse_evpn_neighbors.
from semantic_parser.evpn_parser import parse_evpn_neighbors

# from load_input_expected import load_expected_yaml to load YAML file.
from utils.load_input_expected import (    
    load_expected_yaml
)

BASE_DIR = Path(__file__).resolve().parents[2]
YAML_DIR = BASE_DIR / "yaml"

def check_evpn_neighbors(
    device_name: str,
    routing_summary_file: Path,
):
    print(f"\n==== Checking EVPN on {device_name} ====")

    evpn_facts = parse_evpn_neighbors(routing_summary_file)
    print_evpn_neighbors(device_name, evpn_facts)

    evpn_issues = {}

    # Step1: Mark the peer status.
    for evpn_peer, evpn_info in evpn_facts.items():
        if evpn_info.get("up_down") != "up":
            evpn_issues[evpn_peer] = "EVPN_NEIGHBOR_DOWN"
        # Semantic EVPN neighbor facts (from evpn_parser)
        # {
        #   "10.0.0.1": {
        #     "neighbor_state": "Established",
        #     "up_down": "up",
        #     "uptime": "1d02h"
        #   },
        #   "10.0.0.2": {
        #     "neighbor_state": "Idle",
        #     "up_down": "down",
        #     "uptime": "00:03:12"
        #   }
        # }

    # Step2: if no nodes in the evpn_issues_dicts
    if not evpn_issues:
        return {
            "has_issue": False,
            "protocol": "EVPN",
            "issue_summary": [],
            "issue_detail": None,
            "affected_peers": [],
            "actions": [],
        }

    # Step3: if no nodes in the evpn_issues_dicts
    evpn_issue_summary = list(set(evpn_issues.values())) #["EVPN_NEIGHBOR_DOWN"]
    evpn_affected_peers = list(evpn_issues.keys()) #["10.0.0.2"]

    # Step4: load YAML template as the behaviour Instruction_List
    action_cfg = load_expected_yaml(
        YAML_DIR / "issue_actions_evpn.yaml",
        "EVPN_NEIGHBOR_DOWN",
    )
        # {
        #   "10.0.0.2": "EVPN_NEIGHBOR_DOWN"
        # }
    evpn_peer_actions = []
    for peer in evpn_affected_peers:
        for act in action_cfg.get("actions", []):
            evpn_peer_actions.append(act.format(peer=peer))

    # return {
    # "has_issue": True,
    # "protocol": "EVPN",
    # "issue_summary": evpn_issue_summary,
    # "issue_detail": {
    #     "neighbors": evpn_nei_status,
    # },
    # "affected_peers": evpn_affected_peers,
    # "actions": evpn_peer_actions,
    # }        

    # Step5: return problems description [list], all evpn peer and each status {evpn neighbor, evpn neighbor status}, problem peer [list] and each action to each peer [list].
    return {
        "has_issue": True,
        "protocol": "EVPN",
        "issue_summary": evpn_issue_summary,
        "issue_detail": {
            "neighbors": evpn_facts,
        },
        "affected_peers": evpn_affected_peers,
        "actions": evpn_peer_actions,
    }

        # {
        #   "has_issue": True,
        #   "protocol": "EVPN",

        #   "issue_summary": [
        #     "EVPN_NEIGHBOR_DOWN"
        #   ],

        #   "issue_detail": {
        #     "neighbors": {
        #       "10.0.0.1": {
        #         "up_down": "up",
        #         "time": "1d02h",
        #         "state/pre": 12
        #       },
        #       "10.0.0.2": {
        #         "up_down": "down",
        #         "time": "00:03:12",
        #         "state/pre": "Idle"
        #       }
        #     }
        #   },

        #   "affected_peers": [
        #     "10.0.0.2"
        #   ],

        #   "actions": [
        #     "clear bgp l2vpn evpn neighbor 10.0.0.2",
        #   ]
        # }



