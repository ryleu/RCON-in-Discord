

import discord
from discord.ext import commands
from mcrcon import MCRcon
import datetime
from io import BytesIO
import traceback

with open("token.txt","r") as file:
    token = file.read()

rcon_bot = commands.Bot("!")

rcon_bot.rcon_cache = {}

class RconCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def login(self,ctx, ip = None, password = None):
        if ctx.guild:
            try:
                await ctx.author.send("RCON login only works in DMs.")
            except:
                await ctx.send("I can't DM you and RCON login is only enabled in DMs")
        else:
            if ip and password:
                self.bot.rcon_cache[ctx.author.id] = {"ip":ip,"pass":password,"expires":datetime.datetime.now() + datetime.timedelta(minutes=10)}
                await ctx.send("Credentials cached!")
            else:
                await ctx.send('Correct usage: `!login "ip" "password"`')

    @commands.command()
    async def run(self, ctx, *, command):
        try:
            creds = self.bot.rcon_cache[ctx.author.id]
        except:
            await ctx.send("You need to log in first using `!login`")
            return
        if creds["expires"] <= datetime.datetime.now():
            self.bot.rcon_cache.pop(ctx.author.id,None)
            await ctx.send("Your credentials have expired. Please log in again.")
            return

        self.bot.rcon_cache[ctx.author.id]["expires"] = datetime.datetime.now() + datetime.timedelta(minutes=10)

        with MCRcon(creds["ip"],creds["pass"]) as mcr:
            response = mcr.command(command)
            if len(response) <= 1800:
                await ctx.send("Response: ```{}```".format(response))
            else:
                await ctx.send("Response was too long.",file = discord.File(BytesIO(response.encode()),"response.txt"))

@rcon_bot.event #command error handling
async def on_command_error(ctx,err):
    if type(err)!=commands.errors.CommandNotFound:
        errTB = "\n".join(traceback.format_exception(type(err),err,err.__traceback__))
        if len(errTB) > 1000:
            await ctx.send(err,file=discord.File(BytesIO(errTB.encode()),"traceback.txt"))
        else:
            await ctx.send(str(err)+"\n```{}```".format(errTB))

@rcon_bot.event
async def on_ready():
    print("ready!")

rcon_bot.add_cog(RconCog(rcon_bot))

rcon_bot.run(token)
