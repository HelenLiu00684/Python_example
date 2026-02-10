# src/ai/correlator.py
from src.ai.explainer import generate_explanation

# Layer dependency priority for root cause inference.
#
# Lower values indicate lower-layer components that are more likely
# to be the root cause of failures observed at higher layers.
#
# Design rationale:
# - INTERFACE represents the physical / link layer.
#   Failures at this layer commonly propagate upward and impact
#   all dependent control-plane and overlay protocols.
#
# - OSPF and BGP are underlay routing protocols.
#   They depend on interface availability but may fail independently
#   of overlay protocols.
#
# - EVPN is an overlay control-plane protocol.
#   It depends on a healthy underlay (OSPF/BGP) and interfaces.
#   Therefore, EVPN issues are less likely to be the true root cause
#   when lower-layer issues are present.
#
# This mapping encodes engineering domain knowledge rather than
# dynamic or statistical inference.
LAYER_PRIORITY = {
    "INTERFACE": 0,
    "OSPF": 1,
    "BGP": 1,
    "EVPN": 2,
}


# def correlate_by_device(entries: list[dict]) -> list[dict]:
def correlate_by_device(entries: list[dict], debug: bool = False) -> list[dict]:
    """
    Correlate operation entries according to operation_schema.yaml
    """

    by_device: dict[str, list[dict]] = {}

    # -------- Step 1: group by device --------
    for entry in entries:
        device = entry.get("device")
        issue = entry.get("issue", {})

        protocol = issue.get("protocol")

        if not device or not protocol:
            # schema uncompletely，AI ignore
            continue

        by_device.setdefault(device, []).append(entry)
    if debug:
        print("\n[DEBUG][Step 1] Issues grouped by device:")
        for dev, dev_entries in by_device.items():
            protocols = [
                e["issue"]["protocol"] for e in dev_entries
            ]
            print(f"  - {dev}: {protocols}")

    results = []

    # -------- Step 2: infer root cause per device --------
    for device, dev_entries in by_device.items():
        sorted_entries = sorted(
            dev_entries,
            key=lambda e: LAYER_PRIORITY.get(
                e["issue"]["protocol"], 99
            )
        )

        root = sorted_entries[0]
        impacted = sorted_entries[1:]
        
        root_protocol = root["issue"]["protocol"]
        detail = root["issue"].get("detail", {})
        impacted_protocols = [
            e["issue"]["protocol"] for e in impacted
        ]

        if debug:
            print(f"\n[DEBUG][Step 2] Root cause inference for device: {device}")
            print(f"  Root protocol: {root_protocol}")
            print(f"  Impacted protocols: {impacted_protocols}")

        explanation = generate_explanation(
            root_protocol=root_protocol,
            detail=detail,
            impacted_protocols=impacted_protocols
        )

        results.append({
            "device": device,
            "root_cause": {
                "protocol": root_protocol,
                "summary": root["issue"].get("summary"),
                "detail": detail,
            },
            "explanation": explanation,
            "impacted_protocols": impacted_protocols,
        })

    return results
