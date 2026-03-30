import requests
import json
import time
import user
#https://data-api.polymarket.com/trades?market=0xb48621f7eba07b0a3eeabc6afb09ae42490239903997b9d412b0f69aeb040c8b this is the endpoint to look
#  at the buy sell activity and you can filter the time with time = 1d
# and the last end point is conditionID of the market
#https://data-api.polymarket.com/trades?market=0xb48621f7eba07b0a3eeabc6afb09ae42490239903997b9d412b0f69aeb040c8b&time=1d&limit=10 this will get the top 10 most recent trades
#https://data-api.polymarket.com/activity?user=0x35bbbad2415fe5e39b12da9a316cdc80b022009b through this you can get users order and stuff like that

SPORTS_IDS = ["100639", "100430", "103131", "1", "3", "4", "5", "7"] 
CRYPTO_IDS = ["21", "22", "23", "101944", "101528", "102071"]
EXCLUDE_STR = ",".join(SPORTS_IDS + CRYPTO_IDS)

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob-api.polymarket.com"
DATA_API = "https://data-api.polymarket.com"
current = int(time.time())
print(int(time.time()))

limit = 20
USER_LIMIT = 50
AMOUNT_LIMIT = 2000
def getMarket():
    response = requests.get(
                            f"{GAMMA_API}/markets",
                            params={
                                    "active": "true",
                                    "closed": "false",
                                    "order": "volume24hr",   # top markets by volume
                                    "ascending": "false",
                                    "exclude_tag_id": EXCLUDE_STR,
                                    "limit": limit
                                }
                            )
    markets = response.json()
    return markets

def getTrades(conditionId):

    response = requests.get (
        f"{DATA_API}/trades",
        params = {
            "market": conditionId,
            "after": current,
            "order": "desc",        # Newest first
            "time": "1d",    # Only trades since yesterday
            "limit": USER_LIMIT,           # Increase from 20 to 500 to see the full "Day"
            "filterType": "CASH",    # Let the API do the heavy lifting
            "filterAmount": AMOUNT_LIMIT,    # Only send me trades > $1000
            "side":"BUY"
        }
    )
    orderData = response.json()
    return orderData

def main():
    #market = getMarket()
    
    seen = set()
    
    while True:
        all_trades=[]
        markets = getMarket()
        
        for m in markets:
            data=getTrades(m["conditionId"])
            all_trades.extend(data)
            time.sleep(0.5)

        for d in all_trades:    
            if d["transactionHash"] in seen:
                continue
            else:
                userWallet=d["transactionHash"]
                seen.add(userWallet)        
                total = d["size"]*d["price"]
                numTrade = user.userData(d["proxyWallet"])
                if (numTrade<21):
                    print(f"{d["slug"]}: {total} Dollars for {d["outcome"]} {d["side"]} By {d["name"]} from wallet {d["proxyWallet"]} on {d["timestamp"]} and {numTrade}")
        time.sleep(10)

if __name__ == "__main__":
    main()