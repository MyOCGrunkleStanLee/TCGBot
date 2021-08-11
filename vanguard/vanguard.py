import requests


def verify_vanguard_db():
    payload = {}
    headers = {}

    url = "https://card-fight-vanguard-api.ue.r.appspot.com/api/v1/cards?pagesize=1000&page=1"
    response = requests.request("GET", url, headers=headers, data=payload)
    content = response.text
    content = content.replace(",", "").replace("[", "").replace("]", "").replace("{", "").replace("}", "")
    content = content.replace("\"", "").replace(":", "").replace("dataid", "").replace(" id", ",").replace(" sets", ",")
    content = content.replace("cardtype", ",").replace(" clan", ",")
    print(content)


