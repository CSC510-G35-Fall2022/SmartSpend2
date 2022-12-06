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

import re
import os
from telebot import types
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
    'search':'Search a product and comapre prices',
    'settle': 'Settle an expense shared with you'
}

def command_limit(message, bot):
    """Starts the limit command"""
    chat_id = message.chat.id
    user_limits['user_telegram_id'] = chat_id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    for c in limit_categories:
        markup.add(c)
    msg = bot.reply_to(message, 'Select Category', reply_markup=markup)
    print('category', msg.text)
    bot.register_next_step_handler(msg, post_limit_category_selection, bot)


def post_limit_category_selection(message, bot):
    """Asks the user for how much the limit is"""
    chat_id = message.chat.id
    selected_limit_category = message.text
    if selected_limit_category != 'View Limits' and selected_limit_category in limit_categories:
        global limit_category
        limit_category = selected_limit_category
        message = bot.send_message(
            chat_id, 'How much limit do you want to set on a {} basis? \n(Enter numeric values only)'.format(str(limit_category)))
        bot.register_next_step_handler(message, post_limit_amount_input, bot)
    elif selected_limit_category == 'View Limits':
        # print("viewing limits for current user")
        view_limits(bot)
    else:
        message = bot.send_message(chat_id, 'Entered wrong input')


def post_limit_amount_input(message, bot):
    """Adds the limit to the database"""
    chat_id = message.chat.id
    amount_entered = message.text
    amount_value = validate_entered_amount(amount_entered)

    user_history = list(db.user_limits.find(
        {'user_telegram_id': user_limits['user_telegram_id']}))

    if len(user_history) == 0:
        user_limits[limit_category] = amount_value
        db.user_limits.insert_one(user_limits)
    else:
        db.user_limits.find_one_and_update({"user_telegram_id": user_limits['user_telegram_id']}, {
                                           '$set': {limit_category: amount_value}}, return_document=ReturnDocument.AFTER)


def view_limits(bot):
    """Views limits for daily, monthly, or yearly"""
    user_history_obj = db.user_limits.find(
        {'user_telegram_id': user_limits['user_telegram_id']})
    for user_history in user_history_obj:
        if 'daily' in user_history and user_history['daily']:
            message = bot.send_message(
                user_limits['user_telegram_id'], 'Your Daily Limit is - {}'.format(user_history['daily']))
        if 'monthly' in user_history and user_history['monthly']:
            message = bot.send_message(
                user_limits['user_telegram_id'], 'Your Montly Limit is - {}'.format(user_history['monthly']))
        if 'yearly' in user_history and user_history['yearly']:
            message = bot.send_message(
                user_limits['user_telegram_id'], 'Your Yearly Limit is - {}'.format(user_history['yearly']))

def validate_entered_amount(amount_entered):
    """Validates a numeric amount"""
    if len(amount_entered) > 0 and len(amount_entered) <= 15:
        if amount_entered.isdigit:
            if re.match("^[0-9]*\\.?[0-9]*$", amount_entered):
                amount = round(float(amount_entered), 2)
                if amount > 0:
                    return str(amount)
    return 0