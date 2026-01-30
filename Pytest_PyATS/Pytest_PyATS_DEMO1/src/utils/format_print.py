# 1. format the EVPN neighbor status:
def print_evpn_neighbors(dev, evpn_nei_status):
    print(f"\n[{dev}] EVPN Neighbor Status")
    print("-" * 60)
    print(f"{'Peer':<15} {'State':<8} {'Up/Down':<10} {'Uptime':<10}")
    print("-" * 60)

    for peer, info in evpn_nei_status.items():
        state = info.get("state/pre", "-")
        up_down = info.get("up_down", "-")
        uptime = info.get("time", "-")

        print(f"{peer:<15} {state:<8} {up_down:<10} {uptime:<10}")

    print("-" * 60)