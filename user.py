#user.py
import json
import requests
#https://data-api.polymarket.com/activity?user=0x35bbbad2415fe5e39b12da9a316cdc80b022009b
#https://data-api.polymarket.com/positions?user=0x35bbbad2415fe5e39b12da9a316cdc80b022009b



DATA_API="https://data-api.polymarket.com"
def userData(userWallet):
    response = requests.get(
        f"{DATA_API}/positions",
        params={
            "user": userWallet
        }
    )

    result = response.json()
    return len(result)


