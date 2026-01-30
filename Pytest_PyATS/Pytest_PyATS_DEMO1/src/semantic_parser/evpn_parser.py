# src/parsers/evpn_parser.py
from utils.routing_summary_parser import status_evpn_nei

def parse_evpn_neighbors(routing_summary_file: str) -> dict:
    """
    EVPN Semantic Parser

    Change older parser to Semantic fact

    Input:
        routing_summary_file (str)

    Output (facts):
        {
          "<peer_ip>": {
              "neighbor_state": "Established" | "Idle" | ...,
              "up_down": "up" | "down",
              "uptime": "1d02h"
          }
        }
    """
    raw = status_evpn_nei(routing_summary_file)

    facts = {}
    for peer, info in raw.items():
        facts[peer] = {
            "neighbor_state": info.get("state/pre"),
            "up_down": info.get("up_down"),
            "uptime": info.get("time"),
        }

    return facts
