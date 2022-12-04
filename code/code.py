
# -*- coding: utf-8 -*-
# from bob_telegram_tools.bot import TelegramBot
# import matplotlib.pyplot as plt

import logging
import re
import os
import pymongo
import telebot
import time
from telebot import types
from datetime import datetime, date, timedelta
from telethon import TelegramClient
import asyncio
from pymongo import MongoClient, ReturnDocument
import os
from dotenv import load_dotenv
import argparse
import Scraped_data
import formatter
from tabulate import tabulate
from command.start import start_and_menu_command
from command.add import command_add
from command.search import command_select
from command.history import show_history
from command.display import command_display
from command.edit import edit1
from command.delete import command_delete
from command.limit import command_limit
from command.limit_cat import command_limitcategory
from command.settle import command_settle
from command.website import command_website


load_dotenv()

api_token = os.getenv('TELEGRAM_BOT_TOKEN')
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
api_username = os.getenv('TELEGRAM_USERNAME')
cluster = os.getenv('MONGO_DB_URL')

mongo_client = MongoClient(cluster)
db = mongo_client.smartSpendDB

# global variables to store user choice, user list, spend categories, etc
user_bills = {}
user_limits = {}
count_ = 0
spend_categories = ['Food', 'Groceries', 'Utilities', 'Transport',
                    'Shopping', 'Miscellaneous', 'Others (Please Specify)']
spendlimit_categories = ['Food', 'Groceries', 'Utilities',
                         'Transport', 'Shopping', 'Miscellaneous', 'View Limits']
spend_display_option = ['Day', 'Month', 'All']
timestamp_format = '%b %d %Y %I:%M%p'
limit_categories = ['daily', 'monthly', 'yearly', 'View Limits']
delete_options = ['Delete All', 'Delete a specific record']

bot = telebot.TeleBot(api_token)

telebot.logger.setLevel(logging.INFO)

@bot.message_handler(commands=['start', 'menu'])
def smart_menu(m):
    return start_and_menu_command(m)


@bot.message_handler(commands=['add'])
def smart_add(message):
    command_add(message, bot)


@bot.message_handler(commands=['search'])
def smart_search(message):
    command_select(message, bot)


@bot.message_handler(commands=['history'])
def smart_history(message):
    show_history(message, bot)


@bot.message_handler(commands=['edit'])
def smart_edit(message):
    edit1(message, bot)


@bot.message_handler(commands=['display'])
def smart_display(message):
    command_display(message, bot)


@bot.message_handler(commands=['delete'])
def smart_delete(message):
    command_delete(message, bot)


@bot.message_handler(commands=['limit'])
def smart_limit(message):
    command_limit(message, bot)


@bot.message_handler(commands=['limitcategory'])
def smart_limit_cat(message):
    command_limitcategory(message, bot)

# Handling /settle command
@bot.message_handler(commands=['settle'])
def smart_settle(message):
    command_settle(message, bot)

    # Handling /settle command
@bot.message_handler(commands=['website'])
def smart_website(message):
    command_website(message, bot)

async def main():
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(3)


if __name__ == '__main__':
    asyncio.run(main())
