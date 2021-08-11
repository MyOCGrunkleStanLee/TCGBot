import requests
from digimon import digimon_db
import asyncio


async def fetch_digimon(cards):
    payload = {}
    headers = {}
    print(cards[0])
    while len(cards) > 1:
        await asyncio.sleep(1)
        url = "https://digimoncard.io/api-public/search.php?card={}".format(cards[0].get("card_number"))
        response = requests.request("GET", url, headers=headers, data=payload)
        content = response.text
        print(content)
        cards.remove(cards[0])
        cards.remove(cards[0])


async def verify_digimon_db():
    url = "https://digimoncard.io/api-public/getAllCards.php?sort=name&series=Digimon Card Game&sortdirection=asc"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    content = response.text.replace("\"name\":", "").replace("\"cardnumber\":", "").replace("\"", "").split(sep="},{")
    content[0] = content[0].replace("[{", "")

    for card in content:
        card = card.split(sep=",")
        await asyncio.sleep(.5)
        url = "https://digimoncard.io/api-public/search.php?n={}&card={}".format(card[0], card[1])
        response = requests.request("GET", url, headers=headers, data=payload)
        cd = response.text.replace("\",\"", ":").replace("&gt", "").replace("&lt", "").replace("\"", "")
        cd = cd.replace("1: ", "1 ").replace("2: ", "2 ").replace("3: ", "3 ").replace("4: ", "4 ").replace("5: ", "5 ")
        cd = cd.replace("6: ", "6 ").replace("7: ", "7 ").replace("8: ", "8 ").replace("9: ", "9 ").replace("}", "")
        cd = cd.replace("l,", "l:").replace(",e", ":e").replace(",p", ":p").replace(",i", ":i").replace(",c", ":c")
        cd = cd.split(sep=":")
        if cd[1] == "No card matching your query was found in the database.":
            print(card)
            continue
        name = cd[1]
        card_type = cd[3]
        color = cd[5]
        stage = cd[7]
        attribute = cd[9]
        level = cd[11]
        play_cost = cd[13][0]
        evolution_cost = cd[15]
        card_rarity = cd[17]
        artist = cd[19]
        dp = cd[21]
        card_number = cd[23]
        main_effect = cd[25]
        source_effect = cd[27]
        amount = len(cd) - 5
        card_sets = cd[31]
        value = 31
        while value <= amount:
            value += 1
            card_sets += cd[value]

        image_url = cd[-2] + ":" + cd[-1][: -1]

        digimon_db.check_card(name=name, card_type=card_type, color=color, stage=stage, attribute=attribute,
                              level=level, play_cost=play_cost, evolution_cost=evolution_cost,
                              card_rarity=card_rarity, artist=artist, dp=dp, card_number=card_number,
                              main_effect=main_effect, source_effect=source_effect, card_sets=card_sets,
                              image_url=image_url)
    print("digimon database verified")
