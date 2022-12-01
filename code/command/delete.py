
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
load_dotenv()

api_token = os.getenv('TELEGRAM_BOT_TOKEN')
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
api_username = os.getenv('TELEGRAM_USERNAME')
cluster = os.getenv('MONGO_DB_URL')

mongo_client = MongoClient(cluster)
db = mongo_client.smartSpendDB

#global variables to store user choice, user list, spend categories, etc
user_bills = {}
user_limits = {}
count_ = 0
spend_categories = ['Food', 'Groceries', 'Utilities', 'Transport', 'Shopping', 'Miscellaneous', 'Others (Please Specify)']
spend_display_option = ['Day', 'Month', 'All']
timestamp_format = '%b %d %Y %I:%M%p'
limit_categories = ['daily', 'monthly', 'yearly', 'View Limits']
delete_options = ['Delete All', 'Delete a specific record']

#set of implemented commands and their description
commands = {
    'menu': 'Display this menu',
    'add': 'Record/Add a new spending',
    'display': 'Show sum of expenditure for the current day/month',
    'history': 'Display spending history',
    'delete': 'Clear/Erase all your records',
    'edit': 'Edit/Change spending details',
    'limit': 'Add daily/monthly/yearly limits for spending',
    'search':'Search a product and compare prices',
    'settle': 'Settle an expense shared with you'
}

def command_delete(message, bot):

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    for c in delete_options:
        markup.add(c)
    msg = bot.send_message(
        message.chat.id, 'Would you like to delete all data or a specific expense?', reply_markup=markup)

    bot.register_next_step_handler(msg, post_delete_selection, bot)



def post_delete_selection(message, bot):
    # print(message.text)
    try:
        chat_id = message.chat.id
        selected_delete_option = message.text

        if (selected_delete_option == delete_options[0]):
            print('delete all')

            db.user_bills.delete_many({'user_telegram_id': message.chat.id})

            bot.send_message(message.chat.id, 'All data deleted.')
        elif (selected_delete_option == delete_options[1]):
            print('delete one')
            num = bot.send_message(
                message.chat.id, "which transaction number would you like to delete")
            bot.register_next_step_handler(num, delete_one_handler, bot)
            user_history = db.user_bills.find(
                {'user_telegram_id': message.chat.id, 'number': 2})
    except Exception as e:
        bot.reply_to(message, 'Oh no! ' + str(e))
        display_text = ""
        for c in commands:  # generate help text out of the commands dictionary defined at the top
            display_text += "/" + c + ": "
            display_text += commands[c] + "\n"
        bot.send_message(chat_id, 'Please select a menu option from below:')
        bot.send_message(chat_id, display_text)


def delete_one_handler(message, bot):
    chat_id = message.chat.id
    record_to_delete = message.text
    print(record_to_delete)
    try:
        db.user_bills.delete_one({'number': int(record_to_delete)})
        bot.send_message(message.chat.id, 'Deleted record successfully')
    except Exception as e:
        bot.reply_to(message, 'Oh no! ' + str(e))

