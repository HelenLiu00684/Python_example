import re
from pathlib import Path


def parse_bgp_neighbors(log_file: str) -> dict:
    path = Path(log_file)
    if not path.exists():
        raise FileNotFoundError(log_file)

    text = path.read_text()

    m = re.search(
        r"#\s*show bgp summary\s*(.+?)(?:\n\S+#|\Z)",
        text,
        flags=re.S | re.I,
    )

    neighbors = {}

    if not m:
        return {
            "protocol": "BGP",
            "neighbors": neighbors,
        }

    block = m.group(1)

    pattern = re.compile(
        r"^\s*(\d+\.\d+\.\d+\.\d+)\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+(\S+)\s+(\S+)\s*$",
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
        "protocol": "BGP",
        "neighbors": neighbors,
    }
