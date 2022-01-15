import database
import tcgplayer
import mysql.connector.errors
import asyncio


class CardData:
    def __init__(self, card_game, name, card_id):
        self.card_game = card_game.lower()
        self.name = name
        self.card_id = card_id
        self.data = None
        self.product_ids = None
        self.links = []
        self.short_links = []
        self.prices = []

    def check_database(self):
        # checks if a card is already in the database and returns True if it is
        bad_characters = {"Я": "R", "Ś": "S", "ā": "a", "ū": "u", "\u200b": "", "♥": ":heart:"}
        for character in bad_characters:
            self.name = self.name.replace(character, bad_characters.get(character))
        try:
            data = database.check_card(self.name, self.card_id, self.card_game)
            if data is not None:
                self.data = data
        except mysql.connector.errors.DatabaseError:
            data = None

        if data is not None:
            return True
        else:
            return False

    def shorten_links(self):
        from requests.exceptions import ReadTimeout
        for link in self.links:
            try:
                n_link = tcgplayer.shorten_url(link)
                if n_link is False:
                    self.short_links.append(link)
                else:
                    self.short_links.append(n_link)
            except ReadTimeout:
                print(f"{self.name} has a link that failed to shorten {link}")
                self.short_links.append(link)

    async def fetch_product_ids(self):
        self.product_ids = await tcgplayer.fetch_product_id(self.name, self.card_game)
        self.product_ids = self.product_ids.get("results")

    async def fetch_pricing_info(self):
        data = await tcgplayer.fetch_card_info(self.product_ids, self.card_id)
        if data[1] is False:
            self.update_card_id(data[0])
            await self.fetch_pricing_info()
            return
        self.links = data[0]
        self.prices = data[1]

    def add_card(self):
        database.add_new_card(self.card_game, self.name, self.card_id, self.data)

    def update_card_id(self, card_id):
        self.card_id = card_id
        database.update_card_number(self.card_game, card_id, self.data.get('main_effect'))

    def update_product_ids(self):
        if self.data is None:
            self.data = database.check_card(card_game=self.card_game, card_number=self.card_id, name=self.name)

        if self.data.get('product_id') != self.product_ids:
            database.update_product_ids(card_game=self.card_game, card_id=self.card_id, product_ids=self.product_ids)

    def update_links(self):
        if self.data is None:
            self.data = database.check_card(card_game=self.card_game, card_number=self.card_id, name=self.name)

        if self.data.get('full_links') != str(self.links):
            self.shorten_links()
            database.update_links(card_game=self.card_game, card_id=self.card_id,
                                  full_links=self.links, short_links=self.short_links)

    def update_pricing_info(self):
        if self.data is None:
            self.data = database.check_card(card_game=self.card_game, card_number=self.card_id, name=self.name)

        if self.data.get('prices') != self.prices:
            database.update_prices(card_game=self.card_game, card_id=self.card_id, prices=self.prices)

    async def process_card(self, ncd):
        if ncd is not None:
            self.data = ncd
            self.add_card()
        await self.fetch_product_ids()
        await self.fetch_pricing_info()
        self.update_product_ids()
        self.update_links()
        self.update_pricing_info()
        return True
