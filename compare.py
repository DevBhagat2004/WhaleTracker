#compare.py
import json
import requests
import positions
import addusers
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob-api.polymarket.com"
DATA_API = "https://data-api.polymarket.com"

def main():
    users = addusers.add()
    users_data=[]
    for user in users:
        user_data = positions.userData(user)
        if user_data is None:
            print(f"{user} returned noting either they dont have any positions or you entered wrong user")
        else:
            users_data.extend(user_data)

    correlation_map={}

    for pos in users_data:
        key = (pos['title'], pos['outcome'])
        if key not in correlation_map:
            correlation_map[key] = set()
        correlation_map[key].add(pos['proxyWallet'])

if __name__ == "__main__":
    main() 


