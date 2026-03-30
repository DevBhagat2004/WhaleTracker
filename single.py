# single.py
# Fetches whale trades for a single market
# CLI mode: runs forever and prints
# Frontend mode: getMarket() and getTop() are called directly by api.py

import requests
import time
import user

GAMMA_API = "https://gamma-api.polymarket.com"
DATA_API  = "https://data-api.polymarket.com"

# ── GLOBAL DEFAULTS (overridable from api.py) ──
DEFAULT_SLUG       = "us-forces-enter-iran-by-march-31-222-191-243-517-878-439-519"
DEFAULT_MIN_AMOUNT = 10000
DEFAULT_LIMIT      = 100
DEFAULT_MAX_POS    = 21


def getMarket(slug=DEFAULT_SLUG):
    """
    Fetch market metadata by slug.
    Frontend passes slug from user input.
    CLI uses DEFAULT_SLUG.
    """
    response = requests.get(
        f"{GAMMA_API}/markets",
        params={"slug": slug}
    )
    return response.json()


def getTop(marketData, min_amount=DEFAULT_MIN_AMOUNT, limit=DEFAULT_LIMIT):
    """
    Fetch recent large BUY trades for a market.
    Frontend passes min_amount and limit from controls.
    CLI uses defaults.
    Returns raw list of trade dicts.
    """
    response = requests.get(
        f"{DATA_API}/trades",
        params={
            "market":       marketData[0]["conditionId"],
            "order":        "desc",
            "time":         "1d",
            "limit":        limit,
            "filterType":   "CASH",
            "filterAmount": min_amount,
            "side":         "BUY",
        }
    )
    return response.json()


def getWhales(marketData, min_amount=DEFAULT_MIN_AMOUNT, limit=DEFAULT_LIMIT, max_pos=DEFAULT_MAX_POS):
    """
    Filters getTop() results by position count.
    Used by both CLI main() and api.py.
    Returns list of whale trade dicts — does NOT print.
    """
    trades = getTop(marketData, min_amount, limit)
    yesterday = int(time.time()) - 86400
    result = []

    for d in trades:
      #  if int(d.get("timestamp", 0)) < yesterday:
       #     continue
        total = d["size"] * d["price"]
        pos_count = user.userData(d["proxyWallet"])
        if pos_count < max_pos:
            d["positionCount"] = pos_count
            d["total"]         = total
            result.append(d)

    return result


# ── CLI MODE ────────────────────────────────────
def main():
    market = getMarket()
    seen   = set()

    print(f"Tracking: {market[0].get('question', DEFAULT_SLUG)}")
    print(f"Min amount: ${DEFAULT_MIN_AMOUNT:,} | Max positions: {DEFAULT_MAX_POS}\n")

    while True:
        whales = getWhales(market)
        for d in whales:
            if d["transactionHash"] in seen:
                continue
            seen.add(d["transactionHash"])
            ts = time.strftime('%H:%M:%S', time.localtime(int(d["timestamp"])))
            print(
                f"${d['total']:,.2f} | {d['outcome']} {d['side']} "
                f"| {d['name']} | {d['proxyWallet'][:10]}... "
                f"| positions: {d['positionCount']} | {ts}"
            )
        time.sleep(10)


if __name__ == "__main__":
    main()