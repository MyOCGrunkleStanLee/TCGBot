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
import vanguard.vanguard
from cogs.commands import Commands


load_dotenv()
try:
    db.connect(os.getenv('DB_HOST'), os.getenv('DB_DATABASE'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD'))
except mysql.connector.Error as err:
    print("Something went wrong: {}".format(err))

if bool(os.getenv('DEBUG')):
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

# set up and info of the bot
description = "A digimon bot with a combat system and a tomagochi mini-game to keep players entertained"
bot = commands.Bot(command_prefix=os.getenv('BOT_PREFIX'), description=description)
bot.add_cog(Commands(bot))
cd = []
active_access_token = {}


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
    fetch_access_token()
    active_access_token.update({"expire_time": str(active_access_token.get("expires_in") + int(time.time()))})
    os.environ["Access_Token"] = active_access_token.get("access_token")
    os.environ["expire_time"] = active_access_token.get("expire_time")

    # vanguard.vanguard.verify_vanguard_db()
    print(time.ctime())
    print('Logged in as {} {}. {} guilds connected'.format(bot.user.name, bot.user.id, len(bot.guilds)))
    print('------')


@bot.event
async def on_message(message):
    if int(os.environ["expire_time"]) > int(float(time.time())):
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

bot.run(os.getenv('DISCORD_TOKEN'))
