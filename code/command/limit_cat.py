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
    'limitcategory': 'Add daily/monthly/yearly limits for spending in a specific category',
    'search':'Search a product and comapre prices',
    'settle': 'Settle an expense shared with you'
}

spendlimit_categories = ['Food', 'Groceries', 'Utilities',
                         'Transport', 'Shopping', 'Miscellaneous', 'View Limits']

def command_limitcategory(message, bot):
    chat_id = message.chat.id
    user_limits['user_telegram_id'] = chat_id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    for c in spendlimit_categories:
        markup.add(c)
    msg = bot.reply_to(message, 'Select Category', reply_markup=markup)
    # print('category', msg)
    bot.register_next_step_handler(msg, post_limit_spendcategory_selection, bot)


def post_limit_spendcategory_selection(message, bot):
    chat_id = message.chat.id
    selected_spend_category = message.text
    if selected_spend_category != 'View Limits' and selected_spend_category in spend_categories:
        global spend_category
        spend_category = selected_spend_category
        message = bot.send_message(
            chat_id, 'How much limit do you want to set for {} category? \n(Enter numeric values only)'.format(str(spend_category)))
        bot.register_next_step_handler(message, post_spendlimit_amount_input, bot)
    elif selected_spend_category == 'View Limits':
        print("viewing Category limits for current user")
        view_spendlimits(bot)
    else:
        message = bot.send_message(chat_id, 'Entered wrong input')


def post_spendlimit_amount_input(message, bot):
    chat_id = message.chat.id
    amount_entered = message.text
    amount_value = validate_entered_amount(amount_entered)

    #db.user_limits.delete_many({'user_telegram_id': message.chat.id})

    user_history = list(db.user_limits.find(
        {'user_telegram_id': user_limits['user_telegram_id']}))

    if len(user_history) == 0:
        user_limits[spend_category] = amount_value
        db.user_limits.insert_one(user_limits)
        print('Added Spend Category Limit record ' +
              str(user_limits) + ' to user_limits collection')
        message = bot.send_message(
            chat_id, 'Added Limit for ' + spend_category+": " + str(amount_value))
    else:
        db.user_limits.find_one_and_update({"user_telegram_id": user_limits['user_telegram_id']}, {
                                           '$set': {spend_category: amount_value}}, return_document=ReturnDocument.AFTER)
        print('Updated Spend Category Limit record ' +
              str(user_limits) + ' to user_limits collection')
        message = bot.send_message(
            chat_id, 'Updated Limit for ' + spend_category+": " + str(amount_value))


def view_spendlimits(bot):
    user_history_obj = db.user_limits.find(
        {'user_telegram_id': user_limits['user_telegram_id']})
    for user_history in user_history_obj:
        if 'Food' in user_history and user_history['Food']:
            message = bot.send_message(
                user_limits['user_telegram_id'], 'Your Food Limit is - {}'.format(user_history['Food']))
        if 'Groceries' in user_history and user_history['Groceries']:
            message = bot.send_message(
                user_limits['user_telegram_id'], 'Your Groceries Limit is - {}'.format(user_history['Groceries']))
        if 'Utilities' in user_history and user_history['Utilities']:
            message = bot.send_message(
                user_limits['user_telegram_id'], 'Your Utilities Limit is - {}'.format(user_history['Utilities']))
        if 'Transport' in user_history and user_history['Transport']:
            message = bot.send_message(
                user_limits['user_telegram_id'], 'Your Transport Limit is - {}'.format(user_history['Transport']))
        if 'Shopping' in user_history and user_history['Shopping']:
            message = bot.send_message(
                user_limits['user_telegram_id'], 'Your Shopping Limit is - {}'.format(user_history['Shopping']))
        if 'Miscellaneous' in user_history and user_history['Miscellaneous']:
            message = bot.send_message(
                user_limits['user_telegram_id'], 'Your Miscellaneous Limit is - {}'.format(user_history['Miscellaneous']))

def validate_entered_amount(amount_entered):
    if len(amount_entered) > 0 and len(amount_entered) <= 15:
        if amount_entered.isdigit:
            if re.match("^[0-9]*\\.?[0-9]*$", amount_entered):
                amount = round(float(amount_entered), 2)
                if amount > 0:
                    return str(amount)
    return 0