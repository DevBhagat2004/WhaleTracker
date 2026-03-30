#positions.py
import json
import requests

#from cli import userWallet
#https://data-api.polymarket.com/activity?user=0x35bbbad2415fe5e39b12da9a316cdc80b022009b
#https://data-api.polymarket.com/positions?user=0x35bbbad2415fe5e39b12da9a316cdc80b022009b

DATA_API = "https://data-api.polymarket.com"

def userData(userWallet):
    try:
        # Sending the GET request to the API
        response = requests.get(
            f"{DATA_API}/positions",
            params={
                "user": userWallet
            }
        )
        
        response.raise_for_status()
        
        result = response.json()
        
        return result
    
    except requests.exceptions.RequestException:
        print(f"Error: The user wallet '{userWallet}' is incorrect.")
        return None
