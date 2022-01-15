from discord.ext import commands
from cogs.commands import Commands
from dotenv import load_dotenv
from mysql import connector
import mysql
import requests
import time
import os
import logging
import sys
import asyncio
from datetime import datetime
import threading
import db
import digimon.digimon

developer = False
load_dotenv()

if bool(os.getenv('DEBUG')):
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

# set up and info of the bot
description = "A bot that allows users to search for cards and displays them with pricing info from TCGPlayer"

if developer is True:
    prefix = os.getenv("Developer_BOT_PREFIX")
else:
    prefix = os.getenv("BOT_PREFIX")

bot = commands.Bot(command_prefix=prefix, description=description)
bot.remove_command('help')
bot.add_cog(Commands(bot))

cd = []
active_access_token = {}


# connects the bot to the SQL database
def connect():
    try:
        db.connect(os.getenv('DB_HOST'), os.getenv('DB_DATABASE'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD'))
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))


# used to stop people from using admin commands
def qualified(user):
    if user.id == 299605026941173760:  # My Discord ID
        return True


def check_time():
    # This function runs periodically every 1 second to see if its time to run a check on the DB
    threading.Timer(1, check_time).start()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    if current_time == '00:00:00':  # check at midnight for less traffic
        asyncio.run(verify_databases())


check_time()


@bot.command()
async def kill(ctx):
    # admin only command turns off the bot, usually in case of malfunction or updating
    if qualified(ctx.message.author) is False:
        return
    await ctx.send("Shutting down bot.")
    sys.exit()


# gets an access token for TCGPlayer
def fetch_access_token():
    url = "https://api.tcgplayer.com/token"
    header = {"items": "application/x-www-form-urlencoded"}
    data = "grant_type=client_credentials&client_id={}&client_secret={}"\
        .format(os.getenv("Public_Key"), os.getenv("Private_Key"))
    global active_access_token
    active_access_token = requests.request("GET", url, headers=header, data=data).json()


async def verify_databases():
    try:
        await digimon.digimon.verify_digimon_db()

    except mysql.connector.errors.DatabaseError:
        connect()
        await digimon.digimon.verify_digimon_db()


# when the bot has connected to the discord servers it triggers on_ready
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


# when the bot detects a message in discord it triggers on_message
@bot.event
async def on_message(message):

    if int(float(os.environ["expire_time"])) > int(float(time.time())):
        fetch_access_token()
        active_access_token.update({"expire_time": active_access_token.get("expires_in") + time.time()})
        os.environ["Access_Token"] = active_access_token.get("access_token")
        os.environ["expire_time"] = str(active_access_token.get("expire_time"))

    # if the message came from the bot we don't even need to process it
    if message.author == bot.user:
        return

    await bot.process_commands(message)


if developer is True:
    bot.run(os.getenv("Development_Token"))

else:
    bot.run(os.getenv('DISCORD_TOKEN'))

