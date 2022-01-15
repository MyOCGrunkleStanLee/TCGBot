import requests
import asyncio
import tcgplayer
import time
import card

async def verify_digimon_db():
    print(f"performing a verification of the digimon TCG database at {time.ctime()}")
    url = "https://digimoncard.io/api-public/getAllCards.php?sort=name&series=Digimon Card Game&sort=cardnumber"
    payload = {}
    headers = {}
    responses = requests.request("GET", url, headers=headers, data=payload).json()
    for response in responses:
        ncd = None
        c = card.CardData("Digimon", response.get("name"), response.get("cardnumber"))
        in_db = c.check_database()
        if not in_db:
            url = f"https://digimoncard.io/api-public/search.php?n={response.get('name')}&card={response.get('cardnumber')}"
            cd = requests.request("GET", url, headers=headers, data=payload).json()[0]

            ncd = {'name': cd.get("name"), 'card_number': cd.get("cardnumber"), 'color': cd.get("color"),
                   'main_effect': cd.get("maineffect"), 'secondary_effect': cd.get("soureeffect"),
                   'play_cost': cd.get("play_cost"), 'level': cd.get("stage"),
                   'evolution_cost': cd.get("evolution_cost"),
                   'power': cd.get("dp"), 'type': cd.get("type"), 'image_url': cd.get("image_url")}
        await c.process_card(ncd)
        del c
    print(f"completed digimon database verification at {time.ctime()}")

