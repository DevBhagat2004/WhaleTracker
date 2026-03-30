#single.py
import requests
import json
import time
import user
#https://data-api.polymarket.com/trades?market=0xb48621f7eba07b0a3eeabc6afb09ae42490239903997b9d412b0f69aeb040c8b this is the endpoint to look
#  at the buy sell activity and you can filter the time with time = 1d
# and the last end point is conditionID of the market
#https://data-api.polymarket.com/trades?market=0xb48621f7eba07b0a3eeabc6afb09ae42490239903997b9d412b0f69aeb040c8b&time=1d&limit=10 this will get the top 10 most recent trades
#https://data-api.polymarket.com/activity?user=0x35bbbad2415fe5e39b12da9a316cdc80b022009b through this you can get users order and stuff like that


GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob-api.polymarket.com"
DATA_API = "https://data-api.polymarket.com"
current = int(time.time())
print(int(time.time()))
def getMarket():
    response = requests.get(
                            f"{GAMMA_API}/markets",
                            params={
                                    "slug":"us-forces-enter-iran-by-march-31-222-191-243-517-878-439-519"
                                }
                            )
    markets = response.json()
    return markets

def getTop(marketData):

    response = requests.get (
        f"{DATA_API}/trades",
        params = {
            "market": marketData[0]["conditionId"],
            "after": current,
            "order": "desc",        # Newest first
            "time": "1d",    # Only trades since yesterday
            "limit": "100",           # Increase from 20 to 500 to see the full "Day"
            "filterType": "CASH",    # Let the API do the heavy lifting
            "filterAmount": "10000",    # Only send me trades > $1000
            "side":"BUY"
        }
    )
    orderData = response.json()
    return orderData

def main():
    market = getMarket()
    
    seen = set()
    while True:
        print("Call")
        data=getTop(market)
        for d in data:
            if d["transactionHash"] in seen:
                continue
            else:
                userWallet=d["transactionHash"]
                seen.add(userWallet)        
                total = d["size"]*d["price"]
                numTrade = user.userData(d["proxyWallet"])
                if (numTrade<21):
                    print(f"{total} Dollars for {d["outcome"]} {d["side"]} By {d["name"]} from wallet {d["proxyWallet"]} on {d["timestamp"]} and {numTrade}")
        time.sleep(10)

if __name__ == "__main__":
    main()