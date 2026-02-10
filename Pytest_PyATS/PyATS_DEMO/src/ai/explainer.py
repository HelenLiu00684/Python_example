# src/ai/explainer.py

def generate_explanation(root_protocol, detail, impacted_protocols):
    """
    Generate a human-readable RCA explanation
    based on root cause and impacted protocols.
    """

    # ---- Interface root cause ----
    if root_protocol == "INTERFACE":
        interfaces = detail.get("interfaces", {})
        if interfaces:
            iface = next(iter(interfaces.keys()))
            reason = interfaces[iface].get("raw", "interface failure")

            explanation = (
                f"Interface {iface} is down. "
                f"The failure was detected as: {reason}. "
            )
        else:
            explanation = "An interface-level failure was detected. "

    # ---- EVPN root cause ----
    elif root_protocol == "EVPN":
        explanation = (
            "EVPN neighbor session failure was detected. "
            "No underlying interface or underlay protocol issues "
            "were observed on the device. "
        )

    # ---- Fallback ----
    else:
        explanation = (
            f"{root_protocol} related issue was detected on the device. "
        )

    # ---- Add impact description ----
    if impacted_protocols:
        explanation += (
            "This issue caused impact on the following protocols: "
            + ", ".join(impacted_protocols)
            + "."
        )

    return explanation
