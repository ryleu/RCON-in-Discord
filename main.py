

import discord
from discord.ext import commands, tasks
from mcrcon import MCRcon
import datetime

with open("token.txt","r") as file:
    token = file.read()

rcon_bot = commands.Bot("!")

rcon_bot.rcon_cache = {}

class RconCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.Command()
    async def login(self,ctx, ip = None, pass = None):
        if ctx.guild:
            try:
                await ctx.author.send("RCON login only works in DMs.")
            except:
                await ctx.send("I can't DM you and RCON login is only enabled in DMs")
        else:
            if ip and pass:
                self.bot.rcon_cache[ctx.author.id] = {"ip":ip,"pass":pass,"expires":datetime.datetime.now() + datetime.timedelta(minutes=10)}
                await ctx.send("Credentials cached!")
            else:
                await ctx.send('Correct usage: `!login "ip" "password"`')

    @commands.Command()
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
            await ctx.author.send(mcr.command(command))

@rcon_bot.event()
async def on_ready():
    print("ready!")

@rcon_bot.event()
async def on_command_error(ctx, excep):
    super().on_command_error(ctx, exep)
    await ctx.send(str(excep))

rcon_bot.add_cog(RconCog(rcon_bot))
