
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

# set of implemented commands and their description
commands = {
    'menu': 'Display this menu',
    'add': 'Record/Add a new spending',
    'display': 'Show sum of expenditure for the current day/month',
    'history': 'Display spending history',
    'delete': 'Clear/Erase all your records',
    'edit': 'Edit/Change spending details',
    'limit': 'Add daily/monthly/yearly limits for spending',
    'search': 'Search a product and comapre prices',
    'settle': 'Settle an expense shared with you',
    'limitcategory': 'Set Monthly limits for each spending categories'
}

bot = telebot.TeleBot(api_token)

telebot.logger.setLevel(logging.INFO)


# #Define listener for requests by user
# def listener(user_requests):
# 	for req in user_requests:
# 		if(req.content_type=='text'):
# 			print("{} name: {} chat_id: {} message: {}".format(str(datetime.now()),str(req.chat.first_name),str(req.chat.id),str(req.text)))

# 			# print("{} name: {} chat_id: {} message: {}".format(str(datetime.now()),str(req.chat.first_name),str(req.chat.id)))

# bot.set_update_listener(listener)


@bot.message_handler(commands=['start', 'menu'])
def smart_menu(m):
    return start_and_menu_command(m)

@bot.message_handler(commands=['add'])
def smart_add(message):
    command_add(message, bot)


@bot.message_handler(commands=['search'])
def smart_search(message):
    command_select(message, bot)


# def validate_entered_amount(amount_entered):
#     if len(amount_entered) > 0 and len(amount_entered) <= 15:
#         if amount_entered.isdigit:
#             if re.match("^[0-9]*\\.?[0-9]*$", amount_entered):
#                 amount = round(float(amount_entered), 2)
#                 if amount > 0:
#                     return str(amount)
#     return 0


# async def find_user_by_username(username):
#     try:
#         async with TelegramClient(api_username, api_id, api_hash) as client:
#             await client.start()
#             if not await client.is_user_authorized():
#                 client.send_code_request(api_id)
#             user = await client.get_entity(username)
#             return user
#     except Exception as e:
#         print("Failed to search user, details: ", e)

# # function to fetch expenditure history of the user


@bot.message_handler(commands=['history'])
def smart_history(message):
    show_history(message, bot)


# function to edit date, category or cost of a transaction
@bot.message_handler(commands=['edit'])
def smart_edit(message):
    edit1(message, bot)


# # To send the shared users the updated expense
# async def updating_user_with_updated_expense(message, user_name, user_bills):
#     try:
#         user = await find_user_by_username(user_name)

#         if user == None:
#             return

#         bot.send_message(user.id, 'An expense has been modified.\n The new expense for {} on {} with value of {} was shared with you.'.format(
#             str(user_bills['number']), str(user_bills['category']), str(user_bills['timestamp'].strftime(timestamp_format)), str(user_bills['cost'])))
#     except Exception as e:
#         print("Error during message send to remote user : ", e)


# function to display total expenditure
@bot.message_handler(commands=['display'])
def smart_display(message):
    command_display(message, bot)

# handles "/delete" command


@bot.message_handler(commands=['delete'])
def smart_delete(message):
    command_delete(message, bot)

@bot.message_handler(commands=['limit'])
def command_limit(message):
    chat_id = message.chat.id
    user_limits['user_telegram_id'] = chat_id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    for c in limit_categories:
        markup.add(c)
    msg = bot.reply_to(message, 'Select Category', reply_markup=markup)
    print('category', msg.text)
    bot.register_next_step_handler(msg, post_limit_category_selection)


def post_limit_category_selection(message):
    chat_id = message.chat.id
    selected_limit_category = message.text
    if selected_limit_category != 'View Limits' and selected_limit_category in limit_categories:
        global limit_category
        limit_category = selected_limit_category
        message = bot.send_message(
            chat_id, 'How much limit do you want to set on a {} basis? \n(Enter numeric values only)'.format(str(limit_category)))
        bot.register_next_step_handler(message, post_limit_amount_input)
    elif selected_limit_category == 'View Limits':
        # print("viewing limits for current user")
        view_limits()
    else:
        message = bot.send_message(chat_id, 'Entered wrong input')


def post_limit_amount_input(message):
    chat_id = message.chat.id
    amount_entered = message.text
    amount_value = validate_entered_amount(amount_entered)

    #db.user_limits.delete_many({'user_telegram_id': message.chat.id})

    user_history = list(db.user_limits.find(
        {'user_telegram_id': user_limits['user_telegram_id']}))

    if len(user_history) == 0:
        user_limits[limit_category] = amount_value
        db.user_limits.insert_one(user_limits)
        # print('Added Limit record '+ str(user_limits) +' to user_limits collection')
    else:
        db.user_limits.find_one_and_update({"user_telegram_id": user_limits['user_telegram_id']}, {
                                           '$set': {limit_category: amount_value}}, return_document=ReturnDocument.AFTER)


def view_limits():
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


@bot.message_handler(commands=['limitcategory'])
def command_limitcategory(message):
    chat_id = message.chat.id
    user_limits['user_telegram_id'] = chat_id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    for c in spendlimit_categories:
        markup.add(c)
    msg = bot.reply_to(message, 'Select Category', reply_markup=markup)
    # print('category', msg)
    bot.register_next_step_handler(msg, post_limit_spendcategory_selection)


def post_limit_spendcategory_selection(message):
    chat_id = message.chat.id
    selected_spend_category = message.text
    if selected_spend_category != 'View Limits' and selected_spend_category in spend_categories:
        global spend_category
        spend_category = selected_spend_category
        message = bot.send_message(
            chat_id, 'How much limit do you want to set for {} category? \n(Enter numeric values only)'.format(str(spend_category)))
        bot.register_next_step_handler(message, post_spendlimit_amount_input)
    elif selected_spend_category == 'View Limits':
        print("viewing Category limits for current user")
        view_spendlimits()
    else:
        message = bot.send_message(chat_id, 'Entered wrong input')


def post_spendlimit_amount_input(message):
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


def view_spendlimits():
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


# Handling /settle command
@bot.message_handler(commands=['settle'])
def command_settle(message):
    chat_id = message.chat.id
    message = bot.send_message(
        chat_id, "Please enter the date and time of the transaction you would like to settle in the following format, Eg: Sep 21 2022 1:33PM")
    bot.register_next_step_handler(message, settle_up)


def settle_up(message):
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
        choice_for_settle(message, record)

    except Exception as e:
        bot.reply_to(message, "Oops!" + str(e) +
                     str(e.__cause__) + str(e.__context__))


def choice_for_settle(message, record):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    markup.add("Yes")
    markup.add("No")
    bot.send_message(
        message.chat.id, 'Do you want to settle this bill?', reply_markup=markup)
    bot.register_next_step_handler(message, post_settle_selection, record)


def post_settle_selection(message, record):
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


async def main():
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(3)


if __name__ == '__main__':
    asyncio.run(main())
