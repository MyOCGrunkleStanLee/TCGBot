import requests
import os
import digimon
import time
import asyncio
from pyshorteners import Shortener
import pyshorteners.exceptions

_requests_count = 0
_request_time = time.time()
_searched = []
_category = {'Cardfight Vanguard': 16, }


def track_requests():
    global _requests_count
    global _request_time
    _requests_count += 1
    if int(float(_request_time)) + 60 < int(float(time.time())):
        _request_time = time.time()
        _requests_count = 0
    return _requests_count


def shorten_url(url):
    try:
        return Shortener(api_key=os.getenv('bitly_access_token')).bitly.short(url)

    except pyshorteners.exceptions.ShorteningErrorException:
        return False


async def fetch_response(url, json=None, data=None, post=False):
    if post is False:
        rt = "GET"
    else:
        rt = "POST"

    headers = {"Accept": "application/json",
               "Content-Type": "text/json",
               "Authorization": "bearer " + os.getenv("Access_Token")}

    if track_requests() == 299:
        print(f"TOO MANY REQUESTS WERE MADE ON {str(float(time.time()))}")
        await asyncio.sleep(60)
    if data is None and json is not None:
        response = requests.request(rt, url=url, headers=headers, json=json)
    elif json is None and data is not None:
        response = requests.request(rt, url=url, headers=headers, data=data)
    elif json is None and data is None:
        response = requests.request(rt, url=url, headers=headers, data={})
    else:
        raise ValueError("Both data and json cannot be populated")

    search_response_data = response.json()
    return search_response_data


async def fetch_product_id(card_name, card_game=None):
    if card_name in _searched:
        return {"results": []}
    else:
        _searched.append(card_name)

    url = "https://api.tcgplayer.com/v1.39.0/catalog/categories/63/search"
    json = {"sort": "string", "limit": 100, "offset": 0, "filters": [{"name": "ProductName", "values": [card_name]}]}
    search_response_data = await fetch_response(url, json, post=True)
    return search_response_data


async def set_product_id(data):
    global _searched
    for card in data.get("results"):
        url = f"https://api.tcgplayer.com/catalog/products/{card}?limit=1&getExtendedFields=True"
        response = await fetch_response(url)

        if response.get("results") is not None:
            card_number = response.get("results")[0].get("extendedData")
            if len(card_number) > 2:
                card_number = (card_number[1].get("value") + " N").split(sep=" ")[0]
                digimon.digimon_db.set_product_id_by_card_number(card, card_number)


async def fetch_card_info(product_ids):
    cards = []

    for product_id in product_ids:
        url = f"https://api.tcgplayer.com/pricing/product/{product_id}"
        response = await fetch_response(url)
        for card in response.get("results"):
            if card.get("lowPrice") is not None:
                url = f"https://api.tcgplayer.com/catalog/products/{card.get('productId')}?limit=1&getExtendedFields=True"
                r = await fetch_response(url)
                link = shorten_url(r.get("results")[0].get("url"))
                while link is False:
                    await asyncio.sleep(1)
                    link = shorten_url(r.get("results")[0].get("url"))
                lowest_price = "{}: {}".format(card.get("subTypeName"), card.get("lowPrice"))
                cards.append({product_id: "{}: {}".format(lowest_price, link)})
    return cards

