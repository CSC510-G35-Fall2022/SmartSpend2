#defines how the /new command has to be handled/processed
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
from tabulate import tabulate
load_dotenv()

from telegram.ext import CallbackContext
from telegram import Update

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

bot = telebot.TeleBot(api_token)
telebot.logger.setLevel(logging.INFO)

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

@bot.message_handler(commands=['add'])
def command_add(update: Update, context: CallbackContext):
    chat_id = update.effective_message.chat.id
    user_bills['user_telegram_id'] = chat_id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    for c in spend_categories:
        markup.add(c)
        print(c)
    print(update.effective_message)
    msg = bot.send_message(chat_id=update.effective_chat.id, text='Select Category', reply_to_message_id=update.message.message_id, reply_markup=markup)
    # print('category', msg)
    bot.register_next_step_handler(msg, post_category_selection(update))

def post_category_selection(update):
        # print(message.text)
        chat_id = update.effective_chat.id
        selected_category = update.effective_message.text
        print(selected_category)
        # print(update.effective_message)
        if not selected_category in spend_categories:
            if 'New_Category' in spend_categories:
                spend_categories.remove('New_Category')
                spend_categories.append(selected_category)
                user_bills['category'] = selected_category
                message = bot.send_message(chat_id, 'How much did you spend on {}? \n(Enter numeric values only)'.format(str(selected_category)))
                bot.register_next_step_handler(message, post_amount_input)
            else:
                msg = bot.send_message(chat_id, 'Invalid', reply_markup=types.ReplyKeyboardRemove())
                raise Exception("Sorry I don't recognise this category \"{}\"!".format(selected_category))
        elif str(selected_category) == 'Others (Please Specify)':
            spend_categories.append('New_Category')
            message = bot.send_message(chat_id, 'Please type new category.')
            bot.register_next_step_handler(message, post_category_selection)
        else:
            user_bills['category'] = selected_category
            message = bot.send_message(chat_id, 'How much did you spend on {}? \n(Enter numeric values only)'.format(str(selected_category)))
            # print('message:', message)
            bot.register_next_step_handler(message, post_amount_input)
            # print(post_amount_input)

def post_amount_input(message):
    # print(message.text)
    # try:
    chat_id = message.chat.id
    amount_entered = message.text
    amount_value = validate_entered_amount(amount_entered)  # validate
    if amount_value == 0:  # cannot be $0 spending
        raise Exception("Spent amount has to be a non-zero number.")

    user_bills['cost'] = float(amount_value)
    user_bills['timestamp'] = datetime.now()


    user_history = db.user_bills.find({'user_telegram_id' : message.chat.id})
    maximum = 0
    for rec in user_history:
        maximum = max(maximum, rec['number'])
        # print(maximum)
    # print('done')

    # global count_
    user_bills['number'] = maximum+1
    # count_ += 1

    get_sharing_details(message)

def get_sharing_details(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    markup.add("Yes")
    markup.add("No")
    bot.send_message(message.chat.id, 'Do you want to split this bill with any other users?', reply_markup=markup)
    bot.register_next_step_handler(message, post_sharing_selection)

def post_sharing_selection(message):
    chat_id = message.chat.id
    response = message.text

    if response == "Yes":
        # handle multi-user scenario
        bot.send_message(message.chat.id, 'Enter the username of the other user: ')
        bot.register_next_step_handler(message, handle_user_id_input_for_sharing)

    else:
        # handle direct commit scenario
        add_bill_to_database(message)

def add_bill_to_database(message):
    # print(message)
    chat_id = message.chat.id
    # print(user_bills)
    db.user_bills.insert_one(user_bills)
    # print('Added record '+ str(user_bills) +' to user_bills collection')
    
    bot.send_message(chat_id, 'The following expenditure has been recorded: You have spent $' + str(user_bills['cost']) + ' for ' + str(user_bills['category']) + ' on ' + str(user_bills['timestamp'].strftime(timestamp_format)))
    
        # Check if limits are set and notify if they are crossed.
    limit_history = db.user_limits.find({'user_telegram_id' : user_bills['user_telegram_id']})
    for limit in limit_history:
        if 'daily' in limit:
            start_timestamp = datetime.combine(date.today(), datetime.min.time())
            end_timestamp = start_timestamp + timedelta(days=1)
            records = db.user_bills.aggregate([
                {'$match' : { 'user_telegram_id' : message.chat.id, 'timestamp' : {'$gte':start_timestamp,'$lt': end_timestamp}}},
                {'$group' : {'_id':{'category':'$category'}, 'count':{'$sum':'$cost'}}}
                ])
            if not records:
                bot.send_message(chat_id, 'You have no Daily records')
            else:
                total_spending = 0
                for record in records:
                    total_spending += record['count']
                if total_spending >= float(limit['daily']):
                    bot.send_message(chat_id, 'DAILY LIMIT EXCEEDED. Your daily limit is {}, but you spent {} today'.format(limit['daily'], total_spending))

        if 'monthly' in limit:
            start_timestamp = datetime.combine(date.today().replace(day=1), datetime.min.time())
            end_timestamp = datetime.combine(date.today(), datetime.max.time())
            records = db.user_bills.aggregate([
                {'$match' : { 'user_telegram_id' : message.chat.id, 'timestamp' : {'$gte':start_timestamp,'$lt': end_timestamp}}},
                {'$group' : {'_id':{'category':'$category'}, 'count':{'$sum':'$cost'}}}
            ])
            if not records:
                bot.send_message(chat_id, 'You have no Monthly records')
            else:
                total_spending = 0
                for record in records:
                    total_spending += record['count']
                if total_spending >= float(limit['monthly']):
                    bot.send_message(chat_id, 'MONTHLY LIMIT EXCEEDED. Your Monthly limit is {}, but you spent {} this month'.format(limit['monthly'], total_spending))

        if 'yearly' in limit:
            start_timestamp = datetime.combine(date.today().replace(day=1).replace(month=1), datetime.min.time())
            end_timestamp = datetime.combine(date.today(), datetime.max.time())
            records = db.user_bills.aggregate([
                {'$match' : { 'user_telegram_id' : message.chat.id, 'timestamp' : {'$gte':start_timestamp,'$lt': end_timestamp}}},
                {'$group' : {'_id':{'category':'$category'}, 'count':{'$sum':'$cost'}}}
            ])
            if not records:
                bot.send_message(chat_id, 'You have no Yearly records')
            else:
                total_spending = 0
                for record in records:
                    total_spending += record['count']
                if total_spending >= float(limit['yearly']):
                    bot.send_message(chat_id, 'YEARLY LIMIT EXCEEDED. Your Yearly limit is {}, but you spent {} this year'.format(limit['yearly'], total_spending))
    
    user_bills.clear()

def handle_user_id_input_for_sharing(message):
    chat_id = message.chat.id
    username = str(message.text)

    bot.send_message(chat_id, "User {} will be sent an update about the split".format(username))

    if 'shared_with' in user_bills:
        user_bills['shared_with'].append(username)
    else:
        user_bills['shared_with'] = [username]

    get_sharing_details(message)

    # TODO: Add message queue to handle multiple requests
    asyncio.run(send_update_to_user_about_expense(message, user_bills))

async def send_update_to_user_about_expense(message, user_bills):
    try:
        user = await find_user_by_username(message.text)

        if user == None:
            return

        bot.send_message(user.id, 'An expense for {} on {} with value of {} was shared with you.'.format(str(user_bills['category']), str(user_bills['timestamp'].strftime(timestamp_format)), str(user_bills['cost'])))
    except Exception as e:
        print("Error during message send to remote user : ", e)


async def find_user_by_username(username):
    try:
        async with TelegramClient(api_username, api_id, api_hash) as client:
                await client.start()
                if not await client.is_user_authorized():
                    client.send_code_request(api_id)
                user = await client.get_entity(username)
                return user
    except Exception as e:
        print("Failed to search user, details: ", e)

def validate_entered_amount(amount_entered):
    if len(amount_entered) > 0 and len(amount_entered) <= 15:
        if amount_entered.isdigit:
            if re.match("^[0-9]*\\.?[0-9]*$", amount_entered):
                amount = round(float(amount_entered), 2)
                if amount > 0:
                    return str(amount)
    return 0

