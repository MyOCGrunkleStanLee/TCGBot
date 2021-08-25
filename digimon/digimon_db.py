import db


def check_card(name, card_type, color, stage, attribute, level, play_cost, evolution_cost, card_rarity, artist, dp,
               card_number, main_effect, source_effect, card_sets, image_url):
    con = db.get_connection()
    con.execute("SELECT * FROM digimon WHERE name = %s AND card_number = %s", [name, card_number])

    if con.fetchone() is None:
        con.execute("INSERT INTO digimon (name, type, color, stage, attribute, level, play_cost, evolution_cost,"
                    " card_rarity, artist, dp, card_number, main_effect, source_effect, card_sets, image_url)"
                    " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    [name, card_type, color, stage, attribute, level, play_cost, evolution_cost, card_rarity, artist,
                     dp, card_number, main_effect, source_effect, card_sets, image_url])
        db.commit()


def fetch_card(param):
    if param[0] == "s":
        param = "\\" + param

    con = db.get_connection()
    con.execute("SELECT * FROM digimon WHERE name LIKE \"%{}%\" OR main_effect LIKE \"%{}%\" "
                "OR card_number LIKE \"%{}%\" OR source_effect LIKE \"%{}%\" OR color = %s"
                " OR id = %s OR stage = %s OR type = %s"
                .format(param, param, param, param), [param, param, param, param])
    return con.fetchall()


def fetch_card_by_product_id(product_id):
    con = db.get_connection()
    con.execute("SELECT * FROM digimon WHERE product_id LIKE \"%{}%\"".format(product_id))
    return con.fetchone()


def set_product_id_by_card_number(product_id, card_number):
    con = db.get_connection()
    con.execute("SELECT * FROM digimon WHERE card_number = %s", [card_number])
    data = con.fetchone()
    if data is None or data == []:
        return

    product_id = str(product_id)

    if data.get("product_id") is None:
        con.execute("UPDATE digimon SET product_id = %s WHERE card_number = %s",
                    [product_id, card_number])
        db.commit()
        return

    if data.get("product_id") is not None and (product_id not in data.get("product_id")):
        con.execute("UPDATE digimon SET product_id = %s WHERE card_number = %s",
                    [product_id + ", " + data.get("product_id"), card_number])
        db.commit()
        return


def set_product_id_by_card_name(product_id, card_name):
    con = db.get_connection()
    con.execute("SELECT * FROM digimon WHERE name = %s", [card_name])
    data = con.fetchall()
    if data is None or data == []:
        return

    data = data[0]
    product_id = str(product_id)

    if data.get("product_id") is None:
        con.execute("UPDATE digimon SET product_id = %s WHERE name = %s", [product_id, card_name])
        db.commit()
        return

    if data.get("product_id") is not None and (product_id not in data.get("product_id")):
        con.execute("UPDATE digimon SET product_id = %s WHERE name = %s",
                    [product_id + ", " + data.get("product_id"), card_name])
        db.commit()
        return


def set_price_by_product_id(price, product_id):
    con = db.get_connection()
    con.execute(f"SELECT * FROM digimon WHERE product_id LIKE \"%{product_id}%\"")
    data = con.fetchone()
    if data is None or data == []:
        return

    if data.get("price_info") is not None and data.get("link") is not None:
        price_amount = len(data.get("price_info").split(sep=", "))
        links_amount = len(data.get("link").split(sep=", "))

        if price_amount < links_amount:
            con.execute("UPDATE digimon SET price_info = %s WHERE product_id LIKE \"%{}%\"".format(product_id),
                        [data.get('price_info') + ', ' + str(price)])
            db.commit()

    else:
        con.execute("UPDATE digimon SET price_info = %s WHERE product_id LIKE \"%{}%\"".format(product_id), [price])
        db.commit()


def set_link_by_product_id(link, product_id):
    con = db.get_connection()
    con.execute(f"SELECT * FROM digimon WHERE product_id LIKE \"%{product_id}%\"")
    data = con.fetchone()
    if data is None or data == []:
        return

    if data.get("link") is not None and link not in data.get("link").split(sep=", "):
        con.execute(f"UPDATE digimon SET link = %s WHERE product_id LIKE \"%{product_id}%\"",
                    [data.get('link') + ', ' + link])
        db.commit()

    else:
        con.execute(f"UPDATE digimon SET link = %s WHERE product_id LIKE \"%{product_id}%\"", [link])
        db.commit()
