from bob_telegram_tools.bot import TelegramBot
import matplotlib.pyplot as plt
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

#set of implemented commands and their description
commands = {
    'menu': 'Display this menu',
    'add': 'Record/Add a new spending',
    'display': 'Show sum of expenditure for the current day/month',
    'history': 'Display spending history',
    'delete': 'Clear/Erase all your records',
    'edit': 'Edit/Change spending details',
    'limit': 'Add daily/monthly/yearly limits for spending',
    'search':'Search a product and comapre prices',
    'settle': 'Settle an expense shared with you'
}

def show_history(message, bot):
    try:
        user_history = db.user_bills.find(
            {'user_telegram_id': message.chat.id})
        print(user_history)

        chat_id = message.chat.id
        if user_history is None:
            raise Exception("Sorry! No spending records found!")
        spend_total_str = "Here is your spending history : \n EXPENSE NUMBER |    DATE AND TIME   | CATEGORY | AMOUNT |\n-----------------------------------------------------------------------\n"

        cat = []
        amt = []
        hist_dict = {}
        B = TelegramBot(api_token, chat_id)
        for rec in user_history:
            print(rec)
            cat.append(str(rec['category']))
            amt.append(float(rec['cost']))
            if str(rec['timestamp'].strftime(timestamp_format))[:3] in hist_dict:
                hist_dict[str(rec['timestamp'].strftime(timestamp_format))[
                    :3]] += float(rec['cost'])
            else:
                hist_dict[str(rec['timestamp'].strftime(timestamp_format))[
                    :3]] = float(rec['cost'])
            spend_total_str += '\n{:20s} {:20s} {:20s} {:20s}\n'.format(str(rec['number']), str(
                rec['timestamp'].strftime(timestamp_format)),  str(rec['category']),  str(rec['cost']))
            if 'shared_with' in rec.keys():
                spend_total_str += 'Shared With:'
                for username in rec['shared_with']:
                    spend_total_str += ' {}'.format(str(username))
                spend_total_str += '\n'

        plt.clf()
        month = list(hist_dict.keys())
        exp = list(hist_dict.values())
        plt.bar(range(len(hist_dict)), exp, tick_label=month)
        B.send_plot(plt)
        B.clean_tmp_dir()
        bot.send_message(chat_id, spend_total_str)
    except Exception as e:
        bot.reply_to(message, "Oops!" + str(e) +
                     str(e.__cause__) + str(e.__context__))
