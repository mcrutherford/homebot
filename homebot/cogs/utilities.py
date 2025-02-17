"""
File: utilities.py
Author: Mark Rutherford
Created: 8/4/2021 10:58 PM
"""
import os
import json
from typing import Optional, Union

from dotenv import load_dotenv

VERSION = '1.0.8'

load_dotenv()

def get_env(key: str):
    return os.environ[key] or os.getenv(key)

TOKEN: str = get_env('DISCORD_TOKEN')

# Users
USER_N: int = get_env('USER_N')
USER_M: int = get_env('USER_M')
