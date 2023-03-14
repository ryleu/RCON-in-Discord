#!/bin/env python3

"""
Copyright (c) 2020-2023 Riley <riley@ryleu.me>.
This file is subject to the terms of the GNU General Public License version 3.0, available in the LICENSE file.
"""

import discord
from discord.ext import commands
from mcrcon import MCRcon
import datetime
from io import BytesIO
import traceback
import json

with open("token.json", "r") as file:
    token = json.loads(file.read())["token"]

rcon_bot = commands.Bot("!")

rcon_bot.rcon_cache = {}

class RconCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def login(self, ctx, address = None, password = None):
        # ensure that the login command is only used in DMs
        if ctx.guild:
            try:
                await ctx.author.send("RCON login only works in DMs.")
            except:
                await ctx.send("I can't DM you and RCON login is only enabled in DMs.")
            return

        # ensure that the command is being used properly
        if address and password:
            self.bot.rcon_cache[ctx.author.id] = {
                "address": address,
                "password": password,
                "expiration": datetime.datetime.now() + datetime.timedelta(minutes=10)
            }
            await ctx.send("Credentials cached!")
        else:
            await ctx.send('Correct usage: `!login "address" "password"`')

    @commands.command()
    async def run(self, ctx, *, command):
        # attempt to use cached credentials, restarting the 10 minutes if they're valid
        try:
            credentials = self.bot.rcon_cache[ctx.author.id]
        except IndexError:
            await ctx.send("You need to log in first using `!login`")
            return

        # ensure the credentials are not expired
        if credentials["expiration"] <= datetime.datetime.now():
            self.bot.rcon_cache.pop(ctx.author.id, None)
            await ctx.send("Your credentials have expired. Please log in again.")
            return
        
        self.bot.rcon_cache[ctx.author.id]["expiration"] = datetime.datetime.now() + datetime.timedelta(minutes=10)

        # send the command off to the Minecraft server
        with MCRcon(credentials["address"], credentials["password"]) as connection:
            response = connection.command(command)
            if len(response) <= 1800:
                await ctx.send("Response: ```{}```".format(response))
            else:
                await ctx.send(
                    "Response was too long.",
                    file = discord.File(BytesIO(response.encode()), "response.txt")
                )

@rcon_bot.event
async def on_command_error(ctx, err):
    if type(err) == commands.errors.CommandNotFound: return

    # extract the traceback from the error message and attach it as a file for troubleshooting purposes
    errorTraceback = "\n".join(traceback.format_exception(type(err), err, err.__traceback__))
    await ctx.send(err, file=discord.File(BytesIO(errorTraceback.encode()), "traceback.txt"))

@rcon_bot.event
async def on_ready():
    print("ready!")

rcon_bot.add_cog(RconCog(rcon_bot))

rcon_bot.run(token)
