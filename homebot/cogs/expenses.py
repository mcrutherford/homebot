"""
File: expenses.py
Author: Mark Rutherford
Created: 8/4/2021 9:57 PM
"""
import re
import pickle
import os
import threading
import random

import discord
from discord.ext import commands

from .utilities import get_id_from_name, get_name_from_id, get_payment_percentage_for, USERIDS

EXPENSES_FILE = 'data/expenses.pickle'
MESSAGES_FILE = 'data/expenseMessages.pickle'

PAID_GIFS = [
    "https://tenor.com/view/no-cash-price-priceless-out-of-money-sry-gif-17783887",
    "https://tenor.com/view/no-money-wallet-empty-cashless-gif-16030892",
    "https://tenor.com/view/wallet-broke-poor-no-money-clint-x-morgan-gif-14567018",
    "https://tenor.com/view/i-aint-got-no-cash-man-im-broke-no-money-short-of-funds-no-cash-gif-16053976",
    "https://tenor.com/view/bankrupt-wheel-of-fortune-broke-no-money-poor-gif-16292019",
    "https://tenor.com/view/broke-debt-gif-4486562",
    "https://tenor.com/view/monopoly-money-gif-4907436",
    "https://tenor.com/view/broke-bills-money-gif-10737768",
    "https://tenor.com/view/patrick-star-broke-gif-13045804",
    "https://tenor.com/view/broke-gif-4486559",
    "https://tenor.com/view/broke-broque-high-class-gif-19129970",
    "https://tenor.com/view/no-money-donald-duck-sad-gif-21751594",
    "https://tenor.com/view/cartoons-fox-poor-gif-10729250",
    "https://tenor.com/view/broke-money-lol-funny-no-more-money-gif-7877959",
]


class Expenses(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.expenses: dict[int, float] = {}
        self.lock = threading.Lock()
        self.owe_messages: list[int] = []

        if os.path.isfile(EXPENSES_FILE):
            with open(EXPENSES_FILE, 'rb') as handle:
                self.expenses = pickle.load(handle)

        if os.path.isfile(MESSAGES_FILE):
            with open(MESSAGES_FILE, 'rb') as handle:
                self.owe_messages = pickle.load(handle)

        for uid in USERIDS.keys():
            if uid not in self.expenses:
                self.expenses[uid] = 0

        with open(EXPENSES_FILE, 'wb') as handle:
            pickle.dump(self.expenses, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def _modify_expenses(self, key: int, value: float) -> bool:
        with self.lock:
            if key in self.expenses:
                self.expenses[key] += value
                with open(EXPENSES_FILE, 'wb') as handle:
                    pickle.dump(self.expenses, handle, protocol=pickle.HIGHEST_PROTOCOL)
                return True
        return False

    def get_net_payment_message(self):
        total_expenses = sum(self.expenses.values())
        amount_owed = {}  # The amount of money each person owes
        for uid, paid in self.expenses.items():
            owed = total_expenses * get_payment_percentage_for(uid)
            amount_owed[uid] = owed - paid

        owe_messages = []
        for uid, owed in amount_owed.items():
            name = get_name_from_id(uid).capitalize()
            if owed == 0:
                owe_messages.append(f"{name} doesn't owe anything")
            elif owed > 0:
                owe_messages.append(f"{name} owes ${'{:.2f}'.format(owed)}")
            else:
                owe_messages.append(f"{name} is owed ${'{:.2f}'.format(owed*-1)}")

        message = '- ' + '\n- '.join(owe_messages)
        return message

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        # Ignore messages from itself
        if message.author == self.bot.user:
            return

        # Ignore messages outside allowed channel
        if message.channel.name != 'expenses':
            return

        # Only people who are in the expenses table can interact with these commands
        if message.author.id not in self.expenses.keys():
            return

        # Check if the expenses were paid
        if message.content.lower() == 'paid':
            for uid in self.expenses:
                self._modify_expenses(uid, -self.expenses[uid])
            await message.channel.send(f'Cleared all expenses!')
            await message.channel.send(random.choice(PAID_GIFS))
            await message.delete()
            self.owe_messages = []
            return

        matches = re.search("^(?:([Nn]adine|[Mm]ark) )?\$(-?\d*(?:\.\d\d)?)(?: (.*))?", message.content)
        if matches:
            personid = get_id_from_name(matches.group(1).lower()) if matches.group(1) is not None else message.author.id
            person = get_name_from_id(personid)
            amount = float(matches.group(2))
            reason = matches.group(3) if matches.group(3) is not None else 'None'
            if not personid:
                await message.channel.send('Unknown person to attribute the expense to')
                return

            # Add the expense and send a response message
            if self._modify_expenses(personid, amount):
                for msg_id in self.owe_messages:
                    try:
                        message_to_delete = await message.channel.fetch_message(msg_id)
                        await message_to_delete.delete()
                    except discord.errors.NotFound:
                        print('Attempted to delete already deleted message')
                self.owe_messages = []
                await message.channel.send(f'Logged ${amount} payment from {person.capitalize()} for {reason}')
                new_message = await message.channel.send(self.get_net_payment_message())
                self.owe_messages.append(new_message.id)
                with open(MESSAGES_FILE, 'wb') as handle:
                    pickle.dump(self.owe_messages, handle, protocol=pickle.HIGHEST_PROTOCOL)
                await message.delete()
                return
            else:
                message.channel.send('An error occurred')
        else:
            await message.channel.send('Unable to parse expense')
