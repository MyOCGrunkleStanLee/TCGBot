import requests
import os

access_token = os.getenv("Access_Token")

def fetch_card_price():
    url = "https://api.tcgplayer.com/catalog/categories"
    data = {}
    headers = {"Accept": "application/json", "Authorization": "bearer {}".format(os.getenv("Bearer_Key"))}

    response = requests.request("GET", url=url, headers=headers, data=data)

    print(response.text)

