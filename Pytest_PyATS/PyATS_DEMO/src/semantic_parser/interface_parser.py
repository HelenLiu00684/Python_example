import re
from pathlib import Path


def parse_interfaces(log_file: str) -> dict:
    """
    Parse interface state from device log file.

    This parser is intentionally log-based.
    It derives interface facts from log and show-output lines
    without relying on counters, baselines, or time-series data.

    Input:
        log_file (str): Path to device log summary file

    Output (semantic facts):
        {
          "protocol": "INTERFACE",
          "interfaces": {
            "<interface>": {
              "up": bool,
              "admin_up": bool,
              "oper_up": bool,
              "description": str | None,
              "raw": str | None,
            }
          }
        }
    """
    path = Path(log_file)
    if not path.exists():
        raise FileNotFoundError(log_file)

    text = path.read_text()
    interfaces = {}

    # Match interface operational state lines, e.g.:
    # "Ethernet1/1 is down (err-disabled)"
    # "Ethernet1/2 is up"
    intf_state_re = re.compile(
        r"^(?P<intf>Ethernet[\d/]+)\s+is\s+(?P<state>up|down)",
        re.I,
    )

    # Match err-disable or interface down events from logs, e.g.:
    # "%PM-4-ERRDISABLE: crc-error error detected on Ethernet1/1"
    # "%ETHPORT-5-IF_DOWN: Interface Ethernet1/1, changed state to down"
    err_disable_re = re.compile(
        r"(ERRDISABLE|IF_DOWN).*?(?P<intf>Ethernet[\d/]+)",
        re.I,
    )

    # Step 1:
    # Collect interface up/down state from show-output or log lines.
    # This establishes the primary semantic state.
    for line in text.splitlines():
        line = line.strip()
        m = intf_state_re.match(line)
        if not m:
            continue

        intf = m.group("intf")
        state = m.group("state").lower()
        is_up = state == "up"

        interfaces[intf] = {
            # Semantic interface state
            "up": is_up,

            # In this demo, admin and oper state are derived together.
            # Fine-grained separation is intentionally out of scope.
            "admin_up": is_up,
            "oper_up": is_up,

            # Interface description is not required for v1
            "description": None,

            # Preserve raw evidence for explanation and debugging
            "raw": line,
        }

    # Step 2:
    # Use err-disable or fault logs to refine semantic state.
    # These logs do NOT introduce new interfaces;
    # they only adjust the state of already observed ones.
    for line in text.splitlines():
        m = err_disable_re.search(line)
        if not m:
            continue

        intf = m.group("intf")
        if intf not in interfaces:
            continue

        # Err-disable implies interface is not operationally usable
        interfaces[intf]["up"] = False
        interfaces[intf]["admin_up"] = False
        interfaces[intf]["oper_up"] = False

        # Store the fault log as raw evidence
        interfaces[intf]["raw"] = line.strip()

    return {
        "protocol": "INTERFACE",
        "interfaces": interfaces,
    }
