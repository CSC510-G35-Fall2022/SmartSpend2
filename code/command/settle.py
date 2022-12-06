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

import os
from telebot import types
from datetime import datetime
from pymongo import MongoClient, ReturnDocument
from dotenv import load_dotenv
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

def command_settle(message, bot):
    """Starts the settle command and prompts user for date and time"""
    chat_id = message.chat.id
    message = bot.send_message(
        chat_id, "Please enter the date and time of the transaction you would like to settle in the following format, Eg: Sep 21 2022 1:33PM")
    bot.register_next_step_handler(message, settle_up, bot)


def settle_up(message, bot):
    """Using date and time, allows a user to spend to cover and expense"""
    record = dict()
    timestamp = datetime.strptime(message.text, timestamp_format)

    try:
        user_history = db.user_bills.find(
            {'user_telegram_id': message.chat.id})

        chat_id = message.chat.id
        if user_history is None:
            raise Exception("Sorry! No spending records found!")
        spend_total_str = "Here is your spending history : \n|    DATE AND TIME   | CATEGORY | AMOUNT | SHARED WITH  |\n-----------------------------------------------------------------------\n"
        for rec in user_history:
            # print(str(rec['timestamp'].strftime(timestamp_format)))
            # print(message.text)
            # print(type(rec))
            if (str(rec['timestamp'].strftime(timestamp_format)) == message.text):
                chat_id = message.chat.id
                record['_id'] = rec['_id']
                record['timestamp'] = rec['timestamp']
                record['cost'] = rec['cost']
                record['number'] = rec['number']
                record['category'] = rec['category']
                record['shared_with'] = rec['shared_with']
                spend_total_str += '{:20s} {:20s} {:20s} {}\n'.format(str(rec['number']), str(rec['timestamp'].strftime(timestamp_format)),  str(
                    rec['category']),  str(rec['cost']), str(rec['shared_with'][0]) if 'shared_with' in rec.keys() else "")
        #bot.send_message(chat_id, spend_total_str)
        # print(record)

        bot.send_message(chat_id, 'The following expenditure has been selected to settle up: $' + str(
            record['cost']) + ' for ' + str(record['category']) + ' on ' + str(record['timestamp'].strftime(timestamp_format)))
        bot.send_message(chat_id, 'Your share of the expense is: {}'.format(
            record['cost']/(len(record['shared_with'])+1)))
        choice_for_settle(message, record, bot)

    except Exception as e:
        bot.reply_to(message, "Oops!" + str(e) +
                     str(e.__cause__) + str(e.__context__))


def choice_for_settle(message, record, bot):
    """Confirms if a user wants to settle a bill"""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    markup.add("Yes")
    markup.add("No")
    bot.send_message(
        message.chat.id, 'Do you want to settle this bill?', reply_markup=markup)
    bot.register_next_step_handler(message, post_settle_selection, record, bot)


def post_settle_selection(message, record, bot):
    """Updates the database with the transaction"""
    chat_id = message.chat.id
    response = message.text
    if response == "Yes":
        new_cost = record['cost'] - \
            (record['cost']/(len(record['shared_with'])+1))
        # print(new_cost)
        settled_user_bills = db.user_bills.find_one_and_update({"_id": record['_id']}, {
                                                               '$set': {"cost": float(new_cost)}}, return_document=ReturnDocument.AFTER)
        paid_with_str = "Here is new expense you settled down : \n|    DATE AND TIME   | CATEGORY | AMOUNT TO BE PAID BY OTHERS | SHARED WITH | PAID BY \n-----------------------------------------------------------------------\n"
        paid_with_str += '{:20s} {:20s} {:20s} {:20s}  \n'.format(str(settled_user_bills['timestamp'].strftime(timestamp_format)),  str(
            settled_user_bills['category']),  str(settled_user_bills['cost']), str(settled_user_bills['shared_with']))
        bot.send_message(chat_id, paid_with_str)

    else:
        bot.send_message(chat_id, "You did not select any expense to settle. ")
