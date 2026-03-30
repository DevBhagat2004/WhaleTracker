# compare.py
# Builds a correlation map across multiple whale wallets
# CLI mode: uses addusers.add() for input, prints results
# Frontend mode: correlate(wallets) called directly by api.py

import positions
import addusers


def correlate(wallets):
    """
    Core logic — works for both CLI and frontend.
    Takes a list/set of wallet addresses.
    Returns a sorted list of correlation entries:
    [
      {
        "title":      "Will X happen?",
        "outcome":    "No",
        "wallets":    ["0xAAA", "0xBBB"],
        "count":      2,
        "totalValue": 12500.0,
        "curPrice":   0.88,
      },
      ...
    ]
    Sorted by count descending (most shared positions first).
    """
    users_data = []

    for wallet in wallets:
        data = positions.userData(wallet)
        if data is None:
            print(f"{wallet} returned nothing — invalid wallet or no positions.")
        else:
            users_data.extend(data)

    correlation_map = {}

    for pos in users_data:
        key = (pos["title"], pos["outcome"])

        if key not in correlation_map:
            correlation_map[key] = {
                "title":      pos["title"],
                "outcome":    pos["outcome"],
                "wallets":    [],
                "count":      0,
                "totalValue": 0.0,
                "curPrice":   pos.get("curPrice", 0),
            }

        wallet = pos.get("proxyWallet", "")
        if wallet not in correlation_map[key]["wallets"]:
            correlation_map[key]["wallets"].append(wallet)
            correlation_map[key]["count"] += 1

        correlation_map[key]["totalValue"] += pos.get("currentValue", 0)

    # sort by how many wallets share the position
    return sorted(correlation_map.values(), key=lambda x: x["count"], reverse=True)


# ── CLI MODE ────────────────────────────────────
def main():
    wallets = addusers.add()        # CLI input
    results = correlate(wallets)    # shared logic

    if not results:
        print("No positions found.")
        return

    print(f"\n{'='*70}")
    print(f"CORRELATION MAP — {len(wallets)} wallets")
    print(f"{'='*70}\n")

    for entry in results:
        bar = "█" * entry["count"] + "░" * (len(wallets) - entry["count"])
        print(
            f"[{bar}] {entry['count']}/{len(wallets)} wallets | "
            f"{entry['outcome']:<4} | "
            f"${entry['totalValue']:>10,.2f} | "
            f"{entry['title'][:50]}"
        )

    print(f"\n{'='*70}")


if __name__ == "__main__":
    main()