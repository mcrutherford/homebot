"""
File: homebot.py
Author: Mark Rutherford
Created: 8/4/2021 6:34 PM
"""
import discord
from discord.ext import commands

# Utilities
from cogs.utilities import TOKEN, VERSION

# Cogs
from cogs.school_cancellation import SchoolCancellation

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='?', intents=intents)
bot.add_cog(SchoolCancellation(bot))

@bot.event
async def on_ready():
    print('Version:', VERSION)
    print(f'{bot.user} is connected to the following guilds:')
    for guild in bot.guilds:
        members = '\n - '.join([member.name for member in guild.members])
        print(f'{guild.name}(id: {guild.id})\n - {members}')


@bot.command(name='ping', help='Responds with a pong!')
async def pingpong(ctx):
    await ctx.send('pong!')


@bot.command(name='version', help='Prints the version')
async def get_version(ctx):
    await ctx.send(f"Homebot V{VERSION}")

bot.run(TOKEN)
