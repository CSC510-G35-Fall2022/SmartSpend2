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

def command_add(message, bot):
    chat_id = message.chat.id
    user_bills['user_telegram_id'] = chat_id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    for c in spend_categories:
        markup.add(c)
    markup.add("Cancel")
    msg = bot.reply_to(message, 'Select Category \nSelect Cancel to abort.', reply_markup=markup)
    # print('category', message.text)
    bot.register_next_step_handler(msg, post_category_selection, bot)

def post_category_selection(message, bot):
    # print("hello world")
    try:
        chat_id = message.chat.id
        selected_category = message.text
        if selected_category == "Cancel":
            msg = bot.send_message(chat_id, 'Cancelling record', reply_markup=types.ReplyKeyboardRemove())
            raise Exception("Record Cancelled!!")

        elif not selected_category in spend_categories:
            if 'New_Category' in spend_categories:
                spend_categories.remove('New_Category')
                spend_categories.append(selected_category)
                user_bills['category'] = selected_category
                message = bot.send_message(chat_id, 'How much did you spend on {}? \n(Enter numeric values only Type Cancel to abort!)'.format(str(selected_category)))
                bot.register_next_step_handler(message, post_amount_input, bot)
            else:
                msg = bot.send_message(chat_id, 'Invalid', reply_markup=types.ReplyKeyboardRemove())
                raise Exception("Oh no! Sorry I don't recognise this category \"{}\"!".format(selected_category))
        elif str(selected_category) == 'Others (Please Specify)':
            spend_categories.append('New_Category')
            message = bot.send_message(chat_id, 'Please type new category.')
            bot.register_next_step_handler(message, post_category_selection, bot)
        else:
            user_bills['category'] = selected_category
            message = bot.send_message(chat_id, 'How much did you spend on {}? \n(Enter numeric values only or Type Cancel to abort!)'.format(str(selected_category)))
            # print('message:', message)
            bot.register_next_step_handler(message, post_amount_input, bot)
            # print(post_amount_input)
    except Exception as e:
        bot.reply_to(message,str(e))
        display_text = ""
        for c in commands:  # generate help text out of the commands dictionary defined at the top
            display_text += "/" + c + ": "
            display_text += commands[c] + "\n"
        bot.send_message(chat_id, 'Please select a menu option from below:')
        bot.send_message(chat_id, display_text)

def post_amount_input(message, bot):
    # print(message.text)
    try:
        chat_id = message.chat.id
        amount_entered = message.text
        if amount_entered=='Cancel':
            raise Exception("Cancelling record!!")
        amount_value = validate_entered_amount(amount_entered)  # validate
        if amount_value == 0:  # cannot be $0 spending
            raise Exception("Spent amount has to be a non-zero number.")

        user_bills['cost'] = float(amount_value)
        # print(user_bills)
        # print(user_bills['cost'])

        user_bills['timestamp'] = datetime.now()
        # print(user_bills['timestamp'])
        # print(count)
        # print(user_çcbills['number'])

        user_history = db.user_bills.find({'user_telegram_id' : message.chat.id})
        maximum = 0
        for rec in user_history:
            maximum = max(maximum, rec['number'])
        # print(maximum)
        # print('done')

        # global count_
        user_bills['number'] = maximum+1
        # count_ += 1

        get_sharing_details(message, bot)

    except Exception as e:
        bot.reply_to(message,str(e))
        display_text = ""
        for c in commands:  # generate help text out of the commands dictionary defined at the top
            display_text += "/" + c + ": "
        display_text += commands[c] + "\n"
        bot.send_message(chat_id, 'Please select a menu option from below:')
        bot.send_message(chat_id, display_text)

def get_sharing_details(message, bot):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 3
    markup.add("Yes")
    markup.add("No")
    markup.add("Cancel")
    bot.send_message(message.chat.id, 'Do you want to split this bill with any other users?', reply_markup=markup)
    bot.register_next_step_handler(message, post_sharing_selection, bot)

def post_sharing_selection(message, bot):
    chat_id = message.chat.id
    response = message.text

    if response == "Cancel":
        bot.send_message(message.chat.id, 'Cancelling Record!!')
        display_text = ""
        for c in commands:  # generate help text out of the commands dictionary defined at the top
            display_text += "/" + c + ": "
            display_text += commands[c] + "\n"
        bot.send_message(chat_id, 'Please select a menu option from below:')
        bot.send_message(chat_id, display_text)

    elif response == "Yes":
        # handle multi-user scenario
        bot.send_message(message.chat.id, 'Enter the username of the other user: or Type Cancel to abort!!')
        bot.register_next_step_handler(message, handle_user_id_input_for_sharing, bot)

    else:
        # handle direct commit scenario
        add_bill_to_database(message, bot)

def handle_user_id_input_for_sharing(message, bot):
    chat_id = message.chat.id
    username = str(message.text)

    if username == "Cancel":
        bot.send_message(message.chat.id, 'Cancelling Record!!')
        display_text = ""
        for c in commands:  # generate help text out of the commands dictionary defined at the top
            display_text += "/" + c + ": "
            display_text += commands[c] + "\n"
        bot.send_message(chat_id, 'Please select a menu option from below:')
        bot.send_message(chat_id, display_text)
        return

    bot.send_message(chat_id, "User {} will be sent an update about the split".format(username))

    if 'shared_with' in user_bills:
        user_bills['shared_with'].append(username)
    else:
        user_bills['shared_with'] = [username]

    get_sharing_details(message, bot)

    # TODO: Add message queue to handle multiple requests
    asyncio.run(send_update_to_user_about_expense(message, user_bills, bot))

async def send_update_to_user_about_expense(message, user_bills, bot):
    try:
        user = await find_user_by_username(message.text)

        if user == None:
            return

        bot.send_message(user.id, 'An expense for {} on {} with value of {} was shared with you.'.format(str(user_bills['category']), str(user_bills['timestamp'].strftime(timestamp_format)), str(user_bills['cost'])))
    except Exception as e:
        print("Error during message send to remote user : ", e)

def add_bill_to_database(message, bot):
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

        if 'Food' in limit:
            start_timestamp = datetime.combine(date.today().replace(day=1), datetime.min.time())
            end_timestamp = datetime.combine(date.today(), datetime.max.time())
            records = db.user_bills.aggregate([
                {'$match' : { 'user_telegram_id' : message.chat.id, 'category': 'Food' ,'timestamp' : {'$gte':start_timestamp,'$lt': end_timestamp}}},
                {'$group' : {'_id':{'category':'$category'}, 'count':{'$sum':'$cost'}}}
            ])
            print(records)
            if not records:
                bot.send_message(chat_id, 'You have no Food records')
            else:
                total_spending = 0
                for record in records:
                    total_spending += record['count']
                if total_spending >= float(limit['Food']):
                    bot.send_message(chat_id, 'MONTHLY LIMIT EXCEEDED. Your Monthly Food limit is {}, but you spent {} this month'.format(limit['Food'], total_spending))

        if 'Groceries' in limit:
            start_timestamp = datetime.combine(date.today().replace(day=1), datetime.min.time())
            end_timestamp = datetime.combine(date.today(), datetime.max.time())
            records = db.user_bills.aggregate([
                {'$match' : { 'user_telegram_id' : message.chat.id, 'category': 'Groceries' ,'timestamp' : {'$gte':start_timestamp,'$lt': end_timestamp}}},
                {'$group' : {'_id':{'category':'$category'}, 'count':{'$sum':'$cost'}}}
            ])
            print(records)
            if not records:
                bot.send_message(chat_id, 'You have no Groceries records')
            else:
                total_spending = 0
                for record in records:
                    total_spending += record['count']
                if total_spending >= float(limit['Groceries']):
                    bot.send_message(chat_id, 'MONTHLY LIMIT EXCEEDED. Your Monthly Groceries limit is {}, but you spent {} this month'.format(limit['Groceries'], total_spending))

        if 'Utilities' in limit:
            start_timestamp = datetime.combine(date.today().replace(day=1), datetime.min.time())
            end_timestamp = datetime.combine(date.today(), datetime.max.time())
            records = db.user_bills.aggregate([
                {'$match' : { 'user_telegram_id' : message.chat.id, 'category': 'Utilities' ,'timestamp' : {'$gte':start_timestamp,'$lt': end_timestamp}}},
                {'$group' : {'_id':{'category':'$category'}, 'count':{'$sum':'$cost'}}}
            ])
            print(records)
            if not records:
                bot.send_message(chat_id, 'You have no Utilities records')
            else:
                total_spending = 0
                for record in records:
                    total_spending += record['count']
                if total_spending >= float(limit['Utilities']):
                    bot.send_message(chat_id, 'MONTHLY LIMIT EXCEEDED. Your Monthly Utilities limit is {}, but you spent {} this month'.format(limit['Utilities'], total_spending))

        if 'Transport' in limit:
            start_timestamp = datetime.combine(date.today().replace(day=1), datetime.min.time())
            end_timestamp = datetime.combine(date.today(), datetime.max.time())
            records = db.user_bills.aggregate([
                {'$match' : { 'user_telegram_id' : message.chat.id, 'category': 'Transport' ,'timestamp' : {'$gte':start_timestamp,'$lt': end_timestamp}}},
                {'$group' : {'_id':{'category':'$category'}, 'count':{'$sum':'$cost'}}}
            ])
            print(records)
            if not records:
                bot.send_message(chat_id, 'You have no Groceries records')
            else:
                total_spending = 0
                for record in records:
                    total_spending += record['count']
                if total_spending >= float(limit['Transport']):
                    bot.send_message(chat_id, 'MONTHLY LIMIT EXCEEDED. Your Monthly Transport limit is {}, but you spent {} this month'.format(limit['Transport'], total_spending))

        if 'Shopping' in limit:
            start_timestamp = datetime.combine(date.today().replace(day=1), datetime.min.time())
            end_timestamp = datetime.combine(date.today(), datetime.max.time())
            records = db.user_bills.aggregate([
                {'$match' : { 'user_telegram_id' : message.chat.id, 'category': 'Shopping' ,'timestamp' : {'$gte':start_timestamp,'$lt': end_timestamp}}},
                {'$group' : {'_id':{'category':'$category'}, 'count':{'$sum':'$cost'}}}
            ])
            if not records:
                bot.send_message(chat_id, 'You have no Shopping records')
            else:
                total_spending = 0
                for record in records:
                    total_spending += record['count']
                if total_spending >= float(limit['Shopping']):
                    bot.send_message(chat_id, 'MONTHLY LIMIT EXCEEDED. Your Monthly Shopping limit is {}, but you spent {} this month'.format(limit['Shopping'], total_spending))


    user_bills.clear()

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