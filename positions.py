# positions.py
# Returns full open position data for a wallet
# Works for both terminal and frontend — returns data instead of printing

import requests

DATA_API = "https://data-api.polymarket.com"

def userData(userWallet):
    """
    Returns list of open positions for a wallet.
    Each position has: title, outcome, curPrice, currentValue,
    cashPnl, percentPnl, totalBought, proxyWallet, etc.

    Returns None if wallet is invalid or request fails.
    Works the same for both CLI and frontend.
    """
    try:
        response = requests.get(
            f"{DATA_API}/positions",
            params={"user": userWallet}
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException:
        print(f"Error: wallet '{userWallet}' is incorrect or has no positions.")
        return None