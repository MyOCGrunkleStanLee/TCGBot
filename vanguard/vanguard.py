import requests
import card

# vanguard will be supported one day but currently there are too many challenges to make it feasible

# name, card_number, color, main_effect, secondary_effect, play_cost, level, evolution_cost, power, type, image_url
async def verify_vanguard_db():
    payload = {}
    headers = {}
    for x in range(1, 3):
        url = f"https://card-fight-vanguard-api.ue.r.appspot.com/api/v1/cards?pagesize=1000&page={x}"
        response = requests.request("GET", url, headers=headers, data=payload).json().get("data")
        for cd in response:
            ncd = None
            c = card.CardData(card_game="vanguard", name=cd.get("name"), card_id=None)
            in_db = c.check_database()
            if in_db is False:
                ncd = {'name': cd.get("name"), 'card_number': cd.get("cardnumber"), 'color': cd.get("clan"),
                       'main_effect': cd.get("effect"), 'secondary_effect': None,
                       'play_cost': None, 'level': cd.get("grade"),
                       'evolution_cost': None,
                       'power': cd.get("power"), 'type': cd.get("cardtype"), 'image_url': cd.get("imageurlen")}
                if ncd.get("image_url") == "":
                    continue
            await c.process_card(ncd)
            del c






