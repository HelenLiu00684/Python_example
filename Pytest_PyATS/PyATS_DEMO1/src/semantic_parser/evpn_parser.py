import re
from pathlib import Path


def parse_evpn_neighbors(routing_summary_file: str) -> dict:
    """
    EVPN semantic parser
    Return unified semantic schema
    """
    path = Path(routing_summary_file)
    if not path.exists():
        raise FileNotFoundError(routing_summary_file)

    text = path.read_text()

    m = re.search(
        r"show bgp l2vpn evpn summary(.+?)(?:\n\S+#|\Z)",
        text,
        flags=re.I | re.S,
    )

    neighbors = {}

    if not m:
        return {
            "protocol": "EVPN",
            "neighbors": neighbors,
        }

    block = m.group(1)

    pattern = re.compile(
        r"^\s*(\d+\.\d+\.\d+\.\d+)\s+.*?\s+(\S+)\s+(\d+|Idle|Active|Connect)\s*$",
        flags=re.M,
    )

    for peer, uptime, state_or_pfx in pattern.findall(block):
        if state_or_pfx.isdigit():
            neighbors[peer] = {
                "up": True,
                "uptime": uptime,
                "prefix_count": int(state_or_pfx),
                "fsm_state": None,
                "raw": None,
            }
        else:
            neighbors[peer] = {
                "up": False,
                "uptime": None,
                "prefix_count": None,
                "fsm_state": state_or_pfx,
                "raw": None,
            }

    return {
        "protocol": "EVPN",
        "neighbors": neighbors,
    }
