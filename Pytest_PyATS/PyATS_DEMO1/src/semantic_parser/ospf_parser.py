import re
from pathlib import Path


def parse_ospf_neighbors(routing_summary_file: str) -> dict:
    path = Path(routing_summary_file)
    if not path.exists():
        raise FileNotFoundError(routing_summary_file)

    text = path.read_text()

    m = re.search(
        r"show ip ospf neighbors?\s*\n(?P<body>.*?)(?:\n{2,}\S+#|\Z)",
        text,
        flags=re.I | re.S,
    )

    neighbors = {}

    if not m:
        return {
            "protocol": "OSPF",
            "neighbors": neighbors,
        }

    for line in m.group("body").splitlines():
        line = line.strip()
        if not line or line.lower().startswith(("neighbor id", "ospf")):
            continue

        item = re.match(
            r"^(?P<peer>\d+\.\d+\.\d+\.\d+)\s+\d+\s+(?P<state>\S+/\s*\S+)\s+(?P<uptime>\S+)\s+\S+\s+(?P<intf>\S+)",
            line,
        )
        if not item:
            continue

        peer = item.group("peer")
        state = item.group("state").split("/")[0].upper()

        up = state == "FULL"

        neighbors[peer] = {
            "up": up,
            "uptime": item.group("uptime") if up else None,
            "prefix_count": None,   # OSPF ?????
            "fsm_state": None if up else state,
            "raw": line,
        }

    return {
        "protocol": "OSPF",
        "neighbors": neighbors,
    }
