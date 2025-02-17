"""
File: school_cancellation.py
Author: Mark Rutherford
Created: 02/16/2025
"""
import aiohttp
import asyncio
import discord
from discord.ext import commands
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from .utilities import USER_N

class SchoolCancellation(commands.Cog):
    def __init__(self, bot):
        self.user_id_to_notify = USER_N
        self.channel = 'chat'
        self.url = "https://www.wmur.com/weather/closings"
        self.check_interval = 3 * 60  # Check every 3 minutes
        self.target_string = "Henniker Community School"
        self.linked_url = "https://www.wmur.com/weather/closings#:~:text=Henniker%20Community%20School"

        self.bot = bot
        self.check_task = self.bot.loop.create_task(self.check_website())
        self.last_notification_time = None
        self.last_known_status = None  # To store the last known status

    async def check_website(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.url) as response:
                        if response.status == 200:
                            content = await response.text()
                            soup = BeautifulSoup(content, 'html.parser')

                            # Attempt to find the specific status
                            data_item = soup.find("div", class_="weather-closings-data-item",
                                                  attrs={"data-name": self.target_string})

                            if data_item:
                                status = data_item.find("div", class_="weather-closings-data-status")
                                current_status = status.get_text(strip=True) if status else "Unknown"
                            else:
                                # Fallback to checking for the existence of the target string in the raw content
                                current_status = "Unknown, school found on site" if self.target_string in content else None

                            # Determine if a notification is necessary
                            if current_status:
                                current_time = datetime.now()
                                if (current_status != self.last_known_status) or \
                                (self.last_notification_time is None) or \
                                ((current_time - self.last_notification_time) > timedelta(hours=24)):
                                    channel = discord.utils.get(self.bot.get_all_channels(), name=self.channel)
                                    if channel:
                                        user_mention = f"<@{self.user_id_to_notify}>"
                                        embed = discord.Embed(
                                            title=f"{self.target_string} Status Update :snowflake:",
                                            description=f"[**View status**]({self.linked_url}): ```\n{current_status}\n```",
                                            color=discord.Color.blue()
                                        )

                                        await channel.send(content=user_mention, embed=embed)

                                        # Update the last notification time
                                        self.last_notification_time = current_time

                                    # Update the last known status
                                    self.last_known_status = current_status
            except Exception as e:
                print(f"Error checking website: {e}")

            await asyncio.sleep(self.check_interval)

async def setup(bot):
    await bot.add_cog(SchoolCancellation(bot))
