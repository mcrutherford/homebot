"""
File: homebot.py
Author: Mark Rutherford
Created: 8/4/2021 6:34 PM
"""
import discord
import sayhello


def main():
    print(discord.version_info)
    sayhello.say_hi()


if __name__ == '__main__':
    main()
