from discord.ext import commands
import discord
import digimon
import digimon.digimon_db
import vanguard
import asyncio
import math
import os

_emojis = {
    "back": '◀️',
    "next": '▶️'
}
_color_to_emoji = {"red": "🔴", "yellow": "🟡", "green": "🟢", "blue": "🔵", "purple": "🟣", "white": "⚪", "black": "⚫"}


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def report(self, ctx, *, bug):
        channel = await ctx.bot.fetch_channel(channel_id=878797833044639764)
        await channel.send("{} reports:\n{}".format(ctx.author, bug))
        await ctx.send(f"Thank you for reporting the bug \"{bug}\" it will get looked into as soon as possible!")

    @commands.command()
    async def help(self, ctx):
        await ctx.send(f"Search:\nTo search for a card just do {os.getenv('BOT_PREFIX')}"
                       f"search and a key word some examples of what you can search for are"
                       f" Set, name, effect, type, stage, color, and the bots assigned custom_id"
                       f" (it shows up on the farthest left)\n\nYour search will come up with results and you can react"
                       f" with ◀️ or ▶️ to move the pages forward or backwards.\n\nYou can refine your search simply"
                       f" by typing in another key word, for example if a set was searched type in the name of a card"
                       f" to refine the results to show all the cards with that name in that set.\n\n"
                       f"Once you are down to just one card I'll display for you an image of the card,"
                       f" how much it costs, and a link to buy it. If I tell you that "
                       f"\"There are no current listings for this card\" it probably means the card isn't out yet"
                       f" in english.\n\n Should you run into any bugs please be sure to report them by using "
                       f"{os.getenv('BOT_PREFIX')}report and a clear message as to what the problem is")

    @commands.command()
    async def search(self, ctx, *, parameter):
        if parameter is None:
            await ctx.send("You need to include a parameter to search!")
            return

        search = digimon.digimon_db.fetch_card(parameter)

        async def send_cards(current_page, cards=search, message=None):
            max_on_page = 15
            total_pages = math.ceil(len(cards) / max_on_page)

            def message_check(m):
                if m.author.id == ctx.author.id and m.channel.id == ctx.channel.id:
                    return m.content

            def reaction_add_check(reaction, user):
                return user == ctx.author and \
                       (str(reaction.emoji) == _emojis['back'] or str(reaction.emoji) == _emojis['next']) and \
                       reaction.message.id == message.id

            def reaction_remove_check(reaction):
                return reaction.user_id == ctx.author.id and \
                       (str(reaction.emoji) == _emojis['back'] or str(reaction.emoji) == _emojis['next']) and \
                       reaction.message_id == message.id

            if len(cards) == 0:
                await ctx.send("No cards were found! Make sure there aren't any typos or broaden your search "
                               "and please try again.")
                return
            # header and footer embed
            embed = discord.Embed(title="Cards matching the search \"{}\"".format(parameter).replace("\'", "")
                                  .replace("[", "").replace("]", ""))
            embed.set_footer(text="{} cards total. Page {}/{}".format(len(cards), current_page, total_pages))
            value = ""
            offset = (current_page * max_on_page) - max_on_page
            tmp_cards = cards[offset:offset + max_on_page]
            for x in tmp_cards:
                value += "{}: {}{} {} \n".format(x.get("id"), _color_to_emoji.get(x.get("color").lower()),
                                                      x.get("name"), x.get("card_number"))

            embed.add_field(name="\u200b", value=value)
            if len(cards) == 1:
                if message is not None:
                    await message.remove_reaction(_emojis['next'], message.author)
                    await message.remove_reaction(_emojis['back'], message.author)

                embed.set_footer(text="This product uses TCGplayer data but is not endorsed or certified by TCGplayer.")
                card_number = cards[0].get("card_number")
                if "BT6" in card_number or "EX1" in card_number or "BT7" in card_number:
                    embed.add_field(name="\u200b", value="effect: \n{} \n source effect: \n{}"
                                    .format(cards[0].get("main_effect"), cards[0].get("source_effect")), inline=False)

                embed.add_field(name="\u200b", value="\u200b")
                url = tmp_cards[0].get("image_url").replace("\\", "")
                embed.set_image(url=url)
                value = ""
                prices = cards[0].get("price_info")
                links = cards[0].get("link")
                v = -1

                if prices != [] and prices is not None and links != [] and links is not None:
                    prices = prices.split(sep=", ")
                    links = links.split(sep=", ")
                    for price in prices:
                        v += 1
                        broken_price = price.split(sep=": ")
                        value += "{}: ${}".format(broken_price[0], broken_price[1])

                        if len(broken_price[1]) != 4:
                            value += "0"
                        value += "\n{}\n".format(links[v])
                else:
                    value = "There are no current listings for this card"

                embed.add_field(name="Card price", value=value, inline=False)

            # if there was already embed sent, the user hit next or back edit embed to not spam the channel
            if message is not None:
                await message.edit(embed=embed)
                if len(cards) == 1:
                    return

            # if there is only 1 page there is no need to add the reactions otherwise add them
            else:
                message = await ctx.send(embed=embed)
                if len(cards) == 1:
                    return

                if total_pages > 1:
                    await message.add_reaction(_emojis['back'])
                    await message.add_reaction(_emojis['next'])

            # if there are no reactions we don't need to check for anything
            if total_pages > 1:
                # this returns a true or false: it only returns true when the person who reacted is the original author
                # the reaction is either back or next and that the message they reacted to is the original message
                result = None
                user_reaction = None

                # if they don't react in 1 min timeout and stop looking at that message

                done, pending = await asyncio.wait([
                    ctx.bot.wait_for('message', check=message_check, timeout=60),
                    ctx.bot.wait_for('reaction_add', check=reaction_add_check, timeout=60),
                    ctx.bot.wait_for('raw_reaction_remove', check=reaction_remove_check, timeout=60)
                ], return_when=asyncio.FIRST_COMPLETED)

                try:
                    result = done.pop().result()

                except:
                    pass
                    # If the first finished task died for any reason,
                    # the exception will be replayed here.

                for future in done:
                    # If any exception happened in any other done tasks
                    # we don't care about the exception, but don't want the noise of
                    # non-retrieved exceptions
                    future.exception()

                for future in pending:
                    future.cancel()  # we don't need these anymore

                if result is None:
                    return

                elif _emojis['next'] in str(result):
                    user_reaction = _emojis['next']

                elif _emojis['back'] in str(result):
                    user_reaction = _emojis["back"]

                else:
                    # get a new list of cards based on what the user set as a follow up search
                    search = digimon.digimon_db.fetch_card(result.content)
                    like_cards = []
                    for card in search:
                        if card in cards:
                            like_cards.append(card)

                    current_page = 1
                    return await send_cards(current_page=current_page, message=message, cards=like_cards)

                # if they don't time out we take their reaction and handle it

                if user_reaction:
                    # if its back
                    # and the current page is less than the digimon pages send them to the eggs
                    if user_reaction == _emojis['back']:
                        current_page -= 1

                        if current_page < 1:
                            current_page = total_pages

                    # do the exact same thing just opposite
                    elif user_reaction == _emojis['next']:
                        current_page += 1

                        if current_page > total_pages:
                            current_page = 1
                return await send_cards(current_page=current_page, message=message, cards=cards)

            else:
                await message.remove_reaction(_emojis['next'], message.author)
                await message.remove_reaction(_emojis['back'], message.author)
                if len(cards) > 1:

                    # get a new list of cards based on what the user set as a follow up search
                    try:
                        result = await ctx.bot.wait_for('message', check=message_check, timeout=60)
                    except TimeoutError():
                        return
                    s = digimon.digimon_db.fetch_card(result.content)
                    like_cards = []
                    for card in s:
                        if card in cards:
                            like_cards.append(card)

                    current_page = 1
                    return await send_cards(current_page=current_page, message=message, cards=like_cards)

        # trigger the initial message send with the current page set to 1 as default
        await send_cards(1)
