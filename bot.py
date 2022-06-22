import discord
import os
from discord.ext import commands
from console import Console

_console = Console()

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = ',', intents=intents)
# create a new attribute for the bot called console
client.console = _console


@client.command()
@commands.is_owner()
async def load(ctx, extension):
    client.console.print(f"Loading extension: {extension}", 1)
    client.load_extension(f"cogs.{extension}")

@client.command()
@commands.is_owner()
async def unload(ctx, extension):
    client.console.print(f"Unloading extension: {extension}", 1)
    client.unload_extension(f"cogs.{extension}")

@client.command()
@commands.is_owner()
async def reload(ctx, extension):
    client.console.print(f"Reloading extension: {extension}", 1)
    client.unload_extension(f"cogs.{extension}")
    client.load_extension(f"cogs.{extension}")


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.console.print(f"Loading extension: {filename[:-3]}", 1)
        client.load_extension(f"cogs.{filename[:-3]}")
        

client.run("")