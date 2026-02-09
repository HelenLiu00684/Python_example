def _fmt(val, default="-"):
    """
    Safe formatter for None values
    """
    return default if val is None else val


# =========================
# EVPN
# =========================
def print_evpn_neighbors(device, neighbors: dict):
    print(f"\n[{device}] EVPN Neighbor Status")
    print("-" * 72)
    print(f"{'Peer':<15} {'Up':<6} {'Prefixes':<10} {'Uptime':<10} {'FSM':<12}")
    print("-" * 72)

    for peer, info in neighbors.items():
        print(
            f"{peer:<15} "
            f"{str(info['up']):<6} "
            f"{_fmt(info['prefix_count']):<10} "
            f"{_fmt(info['uptime']):<10} "
            f"{_fmt(info['fsm_state']):<12}"
        )

    print("-" * 72)


# =========================
# BGP
# =========================
def print_bgp_neighbors(device, neighbors: dict):
    print(f"\n[{device}] BGP Neighbor Status")
    print("-" * 72)
    print(f"{'Neighbor':<15} {'Up':<6} {'Prefixes':<10} {'Uptime':<10} {'FSM':<12}")
    print("-" * 72)

    for peer, info in neighbors.items():
        print(
            f"{peer:<15} "
            f"{str(info['up']):<6} "
            f"{_fmt(info['prefix_count']):<10} "
            f"{_fmt(info['uptime']):<10} "
            f"{_fmt(info['fsm_state']):<12}"
        )

    print("-" * 72)


# =========================
# OSPF
# =========================
def print_ospf_neighbors(device, neighbors: dict):
    print(f"\n[{device}] OSPF Neighbor Status")
    print("-" * 72)
    print(f"{'Neighbor':<15} {'Up':<6} {'Uptime':<10} {'FSM':<12}")
    print("-" * 72)

    for peer, info in neighbors.items():
        print(
            f"{peer:<15} "
            f"{str(info['up']):<6} "
            f"{_fmt(info['uptime']):<10} "
            f"{_fmt(info['fsm_state']):<12}"
        )

    print("-" * 72)
