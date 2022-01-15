import requests
import os
import time
import asyncio
from pyshorteners import Shortener
import pyshorteners.exceptions

_requests_count = 0
_request_time = time.time()
_searched = []
_category = {'vanguard': 16, "digimon": 63}


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


async def fetch_product_id(card_name, card_game):
    if card_name in _searched:
        return {"results": []}
    else:
        _searched.append(card_name)
    category_id = _category.get(card_game.lower())
    url = f"https://api.tcgplayer.com/v1.39.0/catalog/categories/{category_id}/search"
    json = {"sort": "string", "limit": 100, "offset": 0, "filters": [{"name": "ProductName", "values": [card_name]}]}
    search_response_data = await fetch_response(url, json, post=True)
    return search_response_data


async def fetch_card_info(product_ids, card_id):
    links = []
    prices = []
    pid = ""
    for product_id in product_ids:
        pid += f"{str(product_id)},"
    if pid == "":
        return [[], []]
    url = f"https://api.tcgplayer.com/catalog/products/{pid[:-1]}?getExtendedFields=True"
    response = await fetch_response(url)
    for result in response.get('results'):
        try:
            number = result.get('extendedData')[1].get('value')
        except IndexError:
            continue
        if card_id is None:
            return [result.get('extendedData')[0].get('value'), False]

        if card_id not in number and number is not None:
            number = result.get('extendedData')[0].get('value')
            if card_id not in number and number is not None:
                continue

        url = f"https://api.tcgplayer.com/pricing/product/{result.get('productId')}"
        response = await fetch_response(url)
        for card in response.get('results'):
            if card.get('lowPrice') is None:
                continue
            links.append(result.get('url'))
            prices.append(card.get('lowPrice'))
    return [links, prices]


