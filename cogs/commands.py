from discord.ext import commands
import discord
import digimon
import digimon.digimon_db
import vanguard
import tcgplayer
import asyncio
import math

_emojis = {
    "back": '◀️',
    "next": '▶️'
}
_color_to_emoji = {"red": "🔴", "yellow": "🟡", "green": "🟢", "blue": "🔵", "purple": "🟣", "white": "⚪", "black": "⚫"}


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def search(self, ctx, *, parameter):
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
                if "BT6" in cards[0].get("card_number"):
                    embed.add_field(name="\u200b", value="effect: \n{} \n source effect: \n{}"
                                    .format(cards[0].get("main_effect"), cards[0].get("source_effect")), inline=False)

                embed.add_field(name="\u200b", value="\u200b")
                url = tmp_cards[0].get("image_url").replace("\\", "")
                embed.set_image(url=url)
                tcgplayer.fetch_card_price()
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

                if _emojis['next'] in str(result):
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
                    # how would i efficiently compare the 2 lists and pull the common values from them?
                    # note that each value inside these lists is a dict
                # if they don't time out we take their reaction and handle it

                if user_reaction:
                    # if its back
                    # and the current page is less than the digimon pages send them to the eggs
                    if user_reaction == _emojis['back']:
                        current_page -= 1

                        if current_page < total_pages:
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
                    result = await ctx.bot.wait_for('message', check=message_check, timeout=60)
                    s = digimon.digimon_db.fetch_card(result.content)
                    like_cards = []
                    for card in s:
                        if card in cards:
                            like_cards.append(card)

                    current_page = 1
                    return await send_cards(current_page=current_page, message=message, cards=like_cards)

        # trigger the initial message send with the current page set to 1 as default
        await send_cards(1)
