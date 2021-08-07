"""
File: expenses.py
Author: Mark Rutherford
Created: 8/4/2021 9:57 PM
"""
import re
import pickle
import os
import threading

import discord
from discord.ext import commands

from .utilities import get_id_from_name, get_name_from_id, get_payment_percentage_for, USERIDS

EXPENSES_FILE = 'data/expenses.pickle'


class Expenses(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.expenses: dict[int, float] = {}
        self.lock = threading.Lock()

        if os.path.isfile(EXPENSES_FILE):
            with open(EXPENSES_FILE, 'rb') as handle:
                self.expenses = pickle.load(handle)

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
            await message.channel.send('Cleared all expenses!')
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
                await message.channel.send(f'Logged ${amount} payment from {person.capitalize()} for {reason}')
                await message.channel.send(self.get_net_payment_message())
            else:
                message.channel.send('An error occurred')
        else:
            await message.channel.send('Unable to parse expense')
