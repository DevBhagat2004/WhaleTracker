# user.py
# Returns position count for a wallet
# Works for both terminal and frontend — no changes needed to call signature

import requests

DATA_API = "https://data-api.polymarket.com"

def userData(userWallet):
    """
    Returns the number of open positions for a wallet.
    Used as a filter — wallets with too many positions are skipped.
    Works the same for both CLI and frontend.
    """
    try:
        response = requests.get(
            f"{DATA_API}/positions",
            params={"user": userWallet}
        )
        response.raise_for_status()
        result = response.json()
        return len(result)
    except requests.exceptions.RequestException:
        return 0  # on error return 0 so it doesn't crash the feed