"""
File: utilities.py
Author: Mark Rutherford
Created: 8/4/2021 10:58 PM
"""
import os
import json
from typing import Optional, Union

from dotenv import load_dotenv

VERSION = '1.0.7'

load_dotenv()
TOKEN: str = os.environ['DISCORD_TOKEN'] or os.getenv('DISCORD_TOKEN')
USERS: dict[str, int] = json.loads(os.environ['USERS'] or os.getenv('USERS'))
PAYMENT_PERCENTAGES: dict[str, int] = json.loads(os.environ['PERCENTAGES'] or os.getenv('PERCENTAGES'))
USERIDS: dict[int, str] = {}
for user_name, user_id in USERS.items():
    USERIDS[user_id] = user_name


def get_id_from_name(name: str) -> Optional[int]:
    if name in USERS:
        return USERS[name]
    else:
        return None


def get_name_from_id(uid: int) -> Optional[str]:
    if uid in USERIDS:
        return USERIDS[uid]
    else:
        return None


def get_payment_percentage_for(person: Union[str, int]) -> Optional[float]:
    name = get_name_from_id(person) if person in USERIDS else person

    if name in PAYMENT_PERCENTAGES:
        return PAYMENT_PERCENTAGES[name]/100
    else:
        return None
