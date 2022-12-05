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
    'search':'Search a product and compare prices',
    'settle': 'Settle an expense shared with you'
}


def command_display(message, bot):
    chat_id = message.chat.id
    user_history = db.user_bills.find({'user_telegram_id': message.chat.id})

    if user_history == None:
        bot.send_message(
            chat_id, "Oops! Looks like you do not have any spending records!")
    else:
        # print(user_history)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row_width = 2
        for mode in spend_display_option:
            markup.add(mode)
        msg = bot.reply_to(
            message, 'Please select a category to see the total expense', reply_markup=markup)
        bot.register_next_step_handler(msg, display_total, bot)


def display_total(message, bot):
    try:
        chat_id = message.chat.id
        display_option = message.text

        if not display_option in spend_display_option:
            raise Exception(
                "Sorry I can't show spendings for \"{}\"!".format(display_option))

        if display_option == 'Day':
            start_timestamp = datetime.combine(
                date.today(), datetime.min.time())
            end_timestamp = start_timestamp + timedelta(days=1)
            records = db.user_bills.aggregate([
                {'$match': {'user_telegram_id': message.chat.id, 'timestamp': {
                    '$gte': start_timestamp, '$lt': end_timestamp}}},
                {'$group': {'_id': {'category': '$category'}, 'count': {'$sum': '$cost'}}}
            ])
        elif display_option == 'Month':
            start_timestamp = datetime.combine(
                date.today().replace(day=1), datetime.min.time())
            end_timestamp = datetime.combine(date.today(), datetime.max.time())
            records = db.user_bills.aggregate([
                {'$match': {'user_telegram_id': message.chat.id, 'timestamp': {
                    '$gte': start_timestamp, '$lt': end_timestamp}}},
                {'$group': {'_id': {'category': '$category'}, 'count': {'$sum': '$cost'}}}
            ])
        elif display_option == 'All':
            # print( db.user_bills.find({'number'}))

            records = db.user_bills.aggregate([
                {'$match': {'user_telegram_id': message.chat.id}},
                {'$group': {'_id': {'category': '$category'}, 'count': {'$sum': '$cost'}}},
                {'$sort': {'number': pymongo.ASCENDING}}
            ])

        if records is None:
            raise Exception(
                "Oops! Looks like you do not have any spending records!")

        total_text = ''
        cat = []
        amt = []
        for record in records:
            total_text += '{:25s} ${}\n'.format(
                record['_id']['category'],  str(record['count']))
            cat.append(record['_id']['category'])
            amt.append(float(record['count']))

        spending_text = ""
        if len(total_text) == 0:
            spending_text = "You have no spendings for {}!".format(
                display_option)
        else:
            spending_text = "Here are your {} total spendings:\n | CATEGORIES | AMOUNT |\n----------------------------------------\n{}".format(
                display_option.lower(), total_text)

        bot.send_message(chat_id, spending_text)
        amt_per = []
        s = sum(amt)
        for i in amt:
            amt_per.append((i/s)*100)

        B = TelegramBot(api_token, chat_id)
        plt.clf()
        plt.pie(amt_per, labels=cat, shadow=True, autopct='%1.1f%%')
        B.send_plot(plt)
        B.clean_tmp_dir()
    except Exception as e:
        bot.reply_to(message, str(e) + str(e.__cause__))