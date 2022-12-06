"""Main code that starts the bot execution"""
# MIT License

# Copyright (c) 2022 CSC510-G35-Fall2022

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# -*- coding: utf-8 -*-
# from bob_telegram_tools.bot import TelegramBot
# import matplotlib.pyplot as plt

import logging
import os
import telebot
import time
import asyncio
from pymongo import MongoClient
from dotenv import load_dotenv
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

import matplotlib.pyplot as plt
plt.switch_backend('Agg') 

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
bot.set_my_commands([
    telebot.types.BotCommand("/start", "Main menu"),
    telebot.types.BotCommand("/add", "Add a new expense"),
    telebot.types.BotCommand("/delete", "Clear/Erase your records"),
    telebot.types.BotCommand("/limit", "Sets limits for a day, month, or year"),
    telebot.types.BotCommand("/limitcategory", "Sets limits for a specific category"),
    telebot.types.BotCommand("/display", "Displays a summary of your expenses"),
    telebot.types.BotCommand("/edit", "Edit one of your display entries"),
    telebot.types.BotCommand("/history", "Shows past expenses"),
    telebot.types.BotCommand("/search", "Scrapes the web for specific items and compares price"),
    telebot.types.BotCommand("/settle", "Settle and expense shared with you"),
    telebot.types.BotCommand("/website", "visit a website to manage expenses")
])

@bot.message_handler(commands=['start', 'menu'])
def smart_menu(m):
    """Executes the start and menu commands"""
    return start_and_menu_command(m)


@bot.message_handler(commands=['add'])
def smart_add(message):
    """Executes the add command"""
    command_add(message, bot)


@bot.message_handler(commands=['search'])
def smart_search(message):
    """Executes the search command to scrape the web for products"""
    command_select(message, bot)


@bot.message_handler(commands=['history'])
def smart_history(message):
    """Executes the history command"""
    show_history(message, bot)


@bot.message_handler(commands=['edit'])
def smart_edit(message):
    """Executes the edit command"""
    edit1(message, bot)


@bot.message_handler(commands=['display'])
def smart_display(message):
    """Executes the display command"""
    command_display(message, bot)


@bot.message_handler(commands=['delete'])
def smart_delete(message):
    """Executes the delete command"""
    command_delete(message, bot)


@bot.message_handler(commands=['limit'])
def smart_limit(message):
    """Executes the limit command"""
    command_limit(message, bot)


@bot.message_handler(commands=['limitcategory'])
def smart_limit_cat(message):
    """Executes the limit command"""
    command_limitcategory(message, bot)

# Handling /settle command
@bot.message_handler(commands=['settle'])
def smart_settle(message):
    """Executes the settle command"""
    command_settle(message, bot)

    # Handling /settle command
@bot.message_handler(commands=['website'])
def smart_website(message):
    """Executes the website command"""
    command_website(message, bot)

async def main():
    """Main method that starts polling"""
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(3)


if __name__ == '__main__':
    asyncio.run(main())
