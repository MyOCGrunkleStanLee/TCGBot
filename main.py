from __future__ import print_function
from discord.ext import commands
from dotenv import load_dotenv
from mysql import connector
import requests
import time
import os
import logging
import db
import mysql
import digimon.digimon
import sys
import vanguard.vanguard
from cogs.commands import Commands

developer = False
load_dotenv()
next_digimon_db_check = int(float(time.time()))

if bool(os.getenv('DEBUG')):
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

# set up and info of the bot
description = "A digimon bot with a combat system and a tomagochi mini-game to keep players entertained"

if developer is True:
    prefix = os.getenv("Developer_BOT_PREFIX")
else:
    prefix = os.getenv("BOT_PREFIX")

bot = commands.Bot(command_prefix=prefix, description=description)
bot.remove_command('help')
bot.add_cog(Commands(bot))

cd = []
active_access_token = {}


def connect():
    try:
        db.connect(os.getenv('DB_HOST'), os.getenv('DB_DATABASE'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD'))
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))


def qualified(user):
    if user.id == 299605026941173760:  # Grunkle
        return True


@bot.command()
async def kill(ctx):
    # admin only command turns off the bot, usually in case of malfunction or updating
    if qualified(ctx.message.author) is False:
        return
    await ctx.send("Shutting down bot.")
    sys.exit()


def fetch_access_token():
    url = "https://api.tcgplayer.com/token"
    header = {"items": "application/x-www-form-urlencoded"}
    data = "grant_type=client_credentials&client_id={}&client_secret={}"\
        .format(os.getenv("Public_Key"), os.getenv("Private_Key"))
    global active_access_token
    active_access_token = requests.request("GET", url, headers=header, data=data).json()



def on_cd(user):
    comp_v = 0
    for author in cd:
        comp_v += 1
        if str(user) in author:
            time1 = time.time()
            time2 = float(author.split()[-1])
            cd.remove(author)
            cd.append(str(user) + " " + str(time.time()))
            if time1 - time2 > .5:
                return False
            else:
                return True
    if comp_v == len(cd):
        cd.append(str(user) + " " + str(time.time()))


@bot.event
async def on_ready():
    connect()
    fetch_access_token()
    active_access_token.update({"expire_time": str(active_access_token.get("expires_in") + int(time.time()))})
    os.environ["Access_Token"] = active_access_token.get("access_token")
    os.environ["expire_time"] = active_access_token.get("expire_time")
    print(time.ctime())
    print('Logged in as {} {}. {} guilds connected'.format(bot.user.name, bot.user.id, len(bot.guilds)))
    print('------')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    if str(error) == "Command raised an exception: OperationalError: MySQL Connection not available.":
        print("sql error")
        connect()
        await bot.process_commands(ctx)

    await ctx.send(f"There has been an error on command {ctx.command} the error is {error} "
                   f"please send a bug report by using {os.getenv('BOT_PREFIX')}report "
                   f"please be as descriptive as possible and it will be resolved as soon as possible."
                   f" Thank you for your understanding!")


@bot.event
async def on_message(message):
    global next_digimon_db_check

    if int(float(os.environ["expire_time"])) > int(float(time.time())):
        fetch_access_token()
        active_access_token.update({"expire_time": active_access_token.get("expires_in") + time.time()})
        os.environ["Access_Token"] = active_access_token.get("access_token")
        os.environ["expire_time"] = str(active_access_token.get("expire_time"))

    # if the message came from the bot we don't even need to process it
    if message.author == bot.user:
        return

    # if the user is spamming we also want to ignore any messages they send
    if on_cd(message.author) is True:
        await message.channel.send("You are sending messages too fast!")
        return

    await bot.process_commands(message)

    if int(float(time.time())) > next_digimon_db_check:
        next_digimon_db_check += 43200
        await digimon.digimon.verify_digimon_db()

if developer is True:
    bot.run(os.getenv("Development_Token"))

else:
    bot.run(os.getenv('DISCORD_TOKEN'))

