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
    con = db.get_connection()

    con.execute("SELECT * FROM digimon WHERE name LIKE \"%{}%\" OR main_effect LIKE \" %{}% \" "
                "OR card_number LIKE \"%{}%\" OR source_effect LIKE \" %{}% \" OR color LIKE %s"
                " OR id = %s OR stage = %s OR type = %s"
                .format(param, param, param, param), [param, param, param, param])
    return con.fetchall()


# con.execute("SELECT * FROM digimon WHERE (name LIKE \"%{}%\ AND color LIKE %s OR id = %s OR card_number = %s"
