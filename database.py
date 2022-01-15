import db
from mysql.connector.errors import DatabaseError


def check_card(name, card_number, card_game):
    con = db.get_connection()
    if card_number is not None:
        con.execute(f"SELECT * FROM {card_game} WHERE name = %s AND card_number = %s", [name, card_number])
    else:
        con.execute(f"SELECT * FROM {card_game} WHERE name = %s", [name])
    card = con.fetchone()
    return card


def add_new_card(card_game, name, card_id, data):
    con = db.get_connection()
    try:
        con.execute(f"INSERT INTO {card_game} (name, card_number, color, main_effect, secondary_effect, "
                    f"play_cost, level, evolution_cost, power, type, image_url) "
                    f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    [name, card_id, data.get("color"), data.get("main_effect"), data.get("secondary_effect"),
                     data.get("play_cost"), data.get("level"), data.get("evolution_cost"), data.get("power"),
                     data.get("type"), data.get("image_url")])

    except DatabaseError:
        con.execute(f"INSERT INTO {card_game} (name, card_number, color, main_effect, secondary_effect, "
                    f"play_cost, level, evolution_cost, power, type, image_url) "
                    f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    [name, card_id, data.get("color"), data.get("main_effect").replace("・", "*"),
                     data.get("secondary_effect"), data.get("play_cost"), data.get("level"), data.get("evolution_cost"),
                     data.get("power"), data.get("type"), data.get("image_url")])

    db.commit()


def update_card_number(card_game, card_id, main_effect):
    con = db.get_connection()
    con.execute(f"UPDATE {card_game} SET card_number = %s WHERE main_effect = %s", [card_id, main_effect])


def update_product_ids(card_game, card_id, product_ids):
    con = db.get_connection()
    con.execute(f"UPDATE {card_game} SET product_id = %s WHERE card_number = %s",
                [str(product_ids), card_id])
    db.commit()


def update_links(card_game, card_id, full_links, short_links):
    con = db.get_connection()
    con.execute(f"UPDATE {card_game} SET full_links = %s WHERE card_number = %s",
                [str(full_links), card_id])
    con.execute(f"UPDATE {card_game} SET short_links = %s WHERE card_number = %s",
                [str(short_links), card_id])
    db.commit()


def update_prices(card_game, card_id, prices):
    con = db.get_connection()
    con.execute(f"UPDATE {card_game} SET prices = %s WHERE card_number = %s",
                [str(prices), card_id])
    db.commit()


def fetch_card(card_game, param):
    if param[0] == "s":
        param = "\\" + param

    con = db.get_connection()
    con.execute("SELECT * FROM {} WHERE name LIKE \"%{}%\" OR main_effect LIKE \"%{}%\" "
                "OR card_number LIKE \"%{}%\" OR secondary_effect LIKE \"%{}%\" OR color = %s"
                " OR id = %s OR level = %s OR type = %s"
                .format(card_game, param, param, param, param), [param, param, param, param])
    return con.fetchall()
