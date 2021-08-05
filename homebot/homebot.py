"""
File: homebot.py
Author: Mark Rutherford
Created: 8/4/2021 6:34 PM
"""
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ['DISCORD_TOKEN'] or os.getenv('DISCORD_TOKEN')


def main():
    print(discord.version_info)
    print(TOKEN)


if __name__ == '__main__':
    main()
