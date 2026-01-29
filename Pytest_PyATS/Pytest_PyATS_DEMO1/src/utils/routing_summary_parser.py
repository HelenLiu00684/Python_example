# utils/routing_summary_parser.py
import re
from pathlib import Path
from typing import Dict



def count_ospf_nei(routing_summary_file: str) -> int:
    """
    Count how many ospf nei existing in the "show ip ospf nei" including the status are unstable. (FULL,Exstart,Down)
    """
    path = Path(routing_summary_file)

    if not path.exists():
        raise FileNotFoundError(f"routing_summary_file not found: {routing_summary_file}")

    routing_summary = path.read_text()

    ospf_match=re.search(r"show ip ospf neighbors(.+?)(\n\n|\Z)",routing_summary,flags=re.S|re.I)#\n\n = one line finished and a empty line || \z = end of the file

    if not ospf_match:
        return 0
    
    ospf_block = ospf_match.group(1)
    ospf_nei= re.findall(r"^\s*\d+\.\d+\.\d+\.\d+",ospf_block,flags=re.M)
    return len(ospf_nei)


def count_bgp_nei(routing_summary_file: str) -> int:
    """
    Count how many bpg nei existing in the "show ip ospf nei" including the status are unstable. (Est,Down)
    """
    path = Path(routing_summary_file)

    if not path.exists():
        raise FileNotFoundError(f"routing_summary_file not found: {routing_summary_file}")

    routing_summary = path.read_text()

    bgp_match=re.search(r"show bgp summary([\s\S]+?)(?=\n\S+#|\Z)",routing_summary,flags=re.S|re.I)#\n\n = one line finished and a empty line || \z = end of the file

    if not bgp_match:
        return 0
    
    bgp_block = bgp_match.group(1)
    #print(bgp_block)
    bgp_nei= re.findall(r"^\s*\d+\.\d+\.\d+\.\d+",bgp_block,flags=re.M)

    return len(bgp_nei)

def status_evpn_nei(routing_summary_file: str) -> dict:
    """
    Return the status of each evpn neighbor status, becasue evpn is belong the family of bgp, only calculate bgp is not enough. (Est,Down)
    """
    path = Path(routing_summary_file)

    if not path.exists():
        raise FileNotFoundError(f"routing_summary_file not found: {routing_summary_file}")

    routing_summary = path.read_text()

    evpn_match=re.search(r"show bgp l2vpn evpn summary(.+?)(\Z)",routing_summary,flags=re.S|re.I)#\n\n = one line finished and a empty line || \z = end of the file

    if not evpn_match:
        return 0
    
    evpn_block = evpn_match.group(1)
    #print(evpn_block)
    
    evpn_neighbors= re.findall(r"^\s*(\d+\.\d+\.\d+\.\d+)\s+.*?\s+(\d+:\d+:\d+|\d+d\d+h)\s+(\d+|Idle|Active|Connect)\s*$",evpn_block,flags=re.M)

    #print(evpn_neighbors)
    result_evpn = {}
    for ip,time,state_prefix in evpn_neighbors:
        if state_prefix.isdigit():
            result_evpn[ip] = {
                "up_down":"up",
                "time":time,
                "state/pre":int(state_prefix)
            }
        else:
            result_evpn[ip] = {
                "up_down":"down",
                "time":time,
                "state/pre":state_prefix
            }
    return result_evpn


def parse_bgp_underlay_summary(log_file: str) -> dict:
    """
    Parse BGP underlay neighbors from log file containing:
      <hostname># show bgp summary
    """

    path = Path(log_file)
    if not path.exists():
        raise FileNotFoundError(f"log file not found: {log_file}")

    text = path.read_text()

    # 1️⃣ 从 CLI 命令开始抓整个 block
    m = re.search(
        r"#\s*show bgp summary\s*(.+?)(?:\n\S+#|\Z)",
        text,
        flags=re.S | re.I,
    )

    if not m:
        return {}

    bgp_block = m.group(1)

    # 2️⃣ 解析 Neighbor 行
    pattern = (
        r"^\s*"
        r"(\d+\.\d+\.\d+\.\d+)\s+"   # Neighbor
        r"\d+\s+"                    # V
        r"\d+\s+"                    # AS
        r"\d+\s+"                    # MsgRcvd
        r"\d+\s+"                    # MsgSent
        r"\d+\s+"                    # TblVer
        r"\d+\s+"                    # InQ
        r"\d+\s+"                    # OutQ
        r"(\S+)\s+"                  # Up/Down
        r"(\S+)\s*$"                 # State/PfxRcd
    )

    neighbors = {}

    for peer, up_down, state_or_pfx in re.findall(pattern, bgp_block, flags=re.M):
        if state_or_pfx.isdigit():
            state = "Established"
            pfx = int(state_or_pfx)
        else:
            state = state_or_pfx
            pfx = 0

        neighbors[peer] = {
            "state": state,
            "up_down": up_down,
            "pfx": pfx,
        }

    return neighbors
# routing_summary_parser.py



def parse_ospf_neighbors_summary(routing_summary_file: str) -> dict:
    """
    Parse ALL OSPF neighbors from 'show ip ospf neighbors' output.
    Fix: handle blank line right after command (spine files have it), and stop at next prompt.
    Return:
      {
        "10.255.0.11": {"state":"FULL", "raw_state":"FULL/ -", "uptime":"1d02h", "address":"...", "interface":"Eth1/1", "raw":"..."},
        ...
      }
    """
    path = Path(routing_summary_file)
    if not path.exists():
        return {}

    text = path.read_text()

    # ✅ robust block capture:
    # - match the command line
    # - allow immediate blank lines
    # - capture until: (two+ blank lines) + (next prompt like "spine1#") OR EOF
    m = re.search(
        r"show ip ospf neighbors?\s*\n"          # command line
        r"(?:\s*\n)*"                            # possible blank lines right after command
        r"(?P<block>.*?)(?:\n{2,}(?=\S+#)|\Z)",   # stop at next prompt or EOF
        text,
        flags=re.I | re.S,
    )
    print(f"the block from ospf is {m}\n")
    if not m:
        return {}

    block = m.group("block")
    neighbors = {}

    for line in block.splitlines():
        line_stripped = line.strip()
        if not line_stripped:
            continue
        if line_stripped.lower().startswith(("ospf process", "total number", "neighbor id")):
            continue

        # Typical NX-OS style:
        # 10.255.0.12  1  EXSTART/ -  00:09:12  172.16.1.6  Eth1/2
        # 10.255.0.14  1  DOWN/ -     00:00:00  172.16.1.14 Eth1/4
        mm = re.match(
            r"^(?P<peer>\d+\.\d+\.\d+\.\d+)\s+"
            r"(?P<pri>\d+)\s+"
            r"(?P<raw_state>\S+/\s*\S+)\s+"
            r"(?P<uptime>\S+)\s+"
            r"(?P<address>\S+)\s+"
            r"(?P<intf>\S+)\s*$",
            line_stripped
        )
        if not mm:
            continue

        peer = mm.group("peer")
        raw_state = mm.group("raw_state")
        # take the part before '/', e.g. "EXSTART" from "EXSTART/-"
        state = raw_state.split("/")[0].strip().upper()

        neighbors[peer] = {
            "state": state,
            "raw_state": raw_state,
            "uptime": mm.group("uptime"),
            "address": mm.group("address"),
            "interface": mm.group("intf"),
            "raw": line_stripped,
        }
    print(f"the result from ospf is {neighbors}\n")
    return neighbors
