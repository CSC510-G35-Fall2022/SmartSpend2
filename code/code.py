#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
from threading import Thread
from tabulate import tabulate
load_dotenv()
from all_commands.start import start_and_menu_command
from all_commands.edit import edit1
from all_commands.add import (command_add, post_category_selection, post_amount_input)

from telegram.ext import (Updater,
                          CommandHandler,
                          ConversationHandler,
                          CallbackQueryHandler,
                          RegexHandler)


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

bot = telebot.TeleBot(api_token)

telebot.logger.setLevel(logging.INFO)

# #Define listener for requests by user
# def listener(user_requests):
# 	for req in user_requests:
# 		if(req.content_type=='text'):
# 			print("{} name: {} chat_id: {} message: {}".format(str(datetime.now()),str(req.chat.first_name),str(req.chat.id),str(req.text)))
           
# 			# print("{} name: {} chat_id: {} message: {}".format(str(datetime.now()),str(req.chat.first_name),str(req.chat.id)))

# bot.set_update_listener(listener)
	
	
@bot.message_handler(commands=['search'])
def command_select(message):
    chat_id = message.chat.id
   
    message = bot.send_message(chat_id, 'what is the product Name?')
    bot.register_next_step_handler(message, product_table)
    

def product_table(message):
    try:
        chat_id = message.chat.id
        product_name = message.text
        bot.send_message(chat_id, 'Loading....')
        bot.send_message(chat_id, 'Compared prices are')
        parser = argparse.ArgumentParser(description="Slash")
        parser.add_argument('--search', type=str, help='Product search query')
        parser.add_argument('--num', type=int, help="Maximum number of records", default=3)
        parser.add_argument('--sort', type=str, nargs='+', help="Sort according to re (relevance: default), pr (price) or ra (rating)", default="re")
        parser.add_argument('--link', action='store_true', help="Show links in the table")
        parser.add_argument('--des', action='store_true', help="Sort in descending (non-increasing) order")
        args = parser.parse_args()
                
        products1 = Scraped_data.searchAmazon(product_name)
        products2 = Scraped_data.searchWalmart(product_name)
        # print(products1)

        for sortBy in args.sort:
            products1 = formatter.sortList(products1, sortBy, args.des)[:args.num]
            products2 = formatter.sortList(products2, sortBy, args.des)[:args.num]
            results = products1 + products2
            results = formatter.sortList(results, sortBy, args.des)
    
        # print(tabulate(results, headers="keys", tablefmt="github"))
        #bot.send_message(chat_id,f'<pre>{table}</pre>', parse_mode=ParseMode.HTML)
        bot.send_message(chat_id, tabulate(results, headers="keys", tablefmt="github"))
    except Exception as e:
        bot.reply_to(message, 'Oh no. ' + str(e))
	
	
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
    

async def send_update_to_user_about_expense(message, user_bills):
    try:
        user = await find_user_by_username(message.text)

        if user == None:
            return

        bot.send_message(user.id, 'An expense for {} on {} with value of {} was shared with you.'.format(str(user_bills['category']), str(user_bills['timestamp'].strftime(timestamp_format)), str(user_bills['cost'])))
    except Exception as e:
        print("Error during message send to remote user : ", e)

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

def validate_entered_amount(amount_entered):
    if len(amount_entered) > 0 and len(amount_entered) <= 15:
        if amount_entered.isdigit:
            if re.match("^[0-9]*\\.?[0-9]*$", amount_entered):
                amount = round(float(amount_entered), 2)
                if amount > 0:
                    return str(amount)
    return 0

#function to fetch expenditure history of the user
@bot.message_handler(commands=['history'])
def show_history(message):
    try:
        user_history = db.user_bills.find({'user_telegram_id' : message.chat.id})
        
        chat_id = message.chat.id
        if user_history is None:
            raise Exception("Sorry! No spending records found!")
        spend_total_str = "Here is your spending history : \n EXPENSE NUMBER |    DATE AND TIME   | CATEGORY | AMOUNT |\n-----------------------------------------------------------------------\n"
        for rec in user_history:
            spend_total_str += '\n{:20s} {:20s} {:20s} {:20s}\n'.format(str(rec['number']), str(rec['timestamp'].strftime(timestamp_format)),  str(rec['category']),  str(rec['cost']))
            if 'shared_with' in rec.keys():
                spend_total_str += 'Shared With:'
                for username in rec['shared_with']:
                    spend_total_str += ' {}'.format(str(username))
                spend_total_str += '\n'
        bot.send_message(chat_id, spend_total_str)
    except Exception as e:
        bot.reply_to(message, "Oops!" + str(e) + str(e.__cause__) + str(e.__context__))	
					
# To send the shared users the updated expense
async def updating_user_with_updated_expense(message,user_name, user_bills):
    try:
        user = await find_user_by_username(user_name)

        if user == None:
            return

        bot.send_message(user.id, 'An expense has been modified.\n The new expense for {} on {} with value of {} was shared with you.'.format(str(user_bills['number']), str(user_bills['category']), str(user_bills['timestamp'].strftime(timestamp_format)), str(user_bills['cost'])))
    except Exception as e:
        print("Error during message send to remote user : ", e)
		

#function to display total expenditure
@bot.message_handler(commands=['display'])
def command_display(message):
    chat_id = message.chat.id
    user_history = db.user_bills.find({'user_telegram_id' : message.chat.id})
    
    if user_history == None:
        bot.send_message(chat_id, "Oops! Looks like you do not have any spending records!")
    else:
        # print(user_history)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row_width = 2
        for mode in spend_display_option:
            markup.add(mode)
        msg = bot.reply_to(message, 'Please select a category to see the total expense', reply_markup=markup)
        bot.register_next_step_handler(msg, display_total)

def display_total(message):
    try:
        chat_id = message.chat.id
        display_option = message.text

        if not display_option in spend_display_option:
            raise Exception("Sorry I can't show spending for \"{}\"!".format(display_option))

        if display_option == 'Day':
            start_timestamp = datetime.combine(date.today(), datetime.min.time())
            end_timestamp = start_timestamp + timedelta(days=1)
            records = db.user_bills.aggregate([
                {'$match' : { 'user_telegram_id' : message.chat.id, 'timestamp' : {'$gte':start_timestamp,'$lt': end_timestamp}}},
                {'$group' : {'_id':{'category':'$category'}, 'count':{'$sum':'$cost'}}}
            ])
        elif display_option == 'Month':
            start_timestamp = datetime.combine(date.today().replace(day=1), datetime.min.time())
            end_timestamp = datetime.combine(date.today(), datetime.max.time())
            records = db.user_bills.aggregate([
                {'$match' : { 'user_telegram_id' : message.chat.id, 'timestamp' : {'$gte':start_timestamp,'$lt': end_timestamp}}},
                {'$group' : {'_id':{'category':'$category'}, 'count':{'$sum':'$cost'}}}
            ])
        elif display_option == 'All':
            # print( db.user_bills.find({'number'}))

            records = db.user_bills.aggregate([
                {'$match' : { 'user_telegram_id' : message.chat.id }},
                {'$group' : {'_id':{'category':'$category'}, 'count':{'$sum':'$cost'}}},
                {'$sort': {'number': pymongo.ASCENDING}}
            ])

        if records is None:
            raise Exception("Oops! Looks like you do not have any spending records!")

        total_text = ''
        for record in records:
            total_text += '{:25s} {}\n'.format(record['_id']['category'],  str(record['count']))

        spending_text = ""
        if len(total_text) == 0:
            spending_text = "You have no spending for {}!".format(display_option)
        else:
            spending_text = "Here are your {} total spending:\n | CATEGORIES | AMOUNT |\n----------------------------------------\n{}".format(display_option.lower(), total_text)

        bot.send_message(chat_id, spending_text)
    except Exception as e:
        bot.reply_to(message, str(e) + str(e.__cause__))

#handles "/delete" command
@bot.message_handler(commands=['delete'])
def command_delete(message):
    db.user_bills.delete_many({'user_telegram_id': message.chat.id})
    bot.send_message(message.chat.id, 'All data deleted.')

@bot.message_handler(commands=['limit'])
def command_limit(message):
    chat_id = message.chat.id
    user_limits['user_telegram_id'] = chat_id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    for c in limit_categories:
        markup.add(c)
    msg = bot.reply_to(message, 'Select Category', reply_markup=markup)
    # print('category', msg)
    bot.register_next_step_handler(msg, post_limit_category_selection)

def post_limit_category_selection(message):
    chat_id = message.chat.id
    selected_limit_category = message.text
    if selected_limit_category != 'View Limits' and selected_limit_category in limit_categories:
        global limit_category
        limit_category = selected_limit_category
        message = bot.send_message(chat_id, 'How much limit do you want to set on a {} basis? \n(Enter numeric values only)'.format(str(limit_category)))
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

    user_history = list(db.user_limits.find({'user_telegram_id' : user_limits['user_telegram_id']}))

    if len(user_history) == 0:
        user_limits[limit_category] = amount_value
        db.user_limits.insert_one(user_limits)
        # print('Added Limit record '+ str(user_limits) +' to user_limits collection')
    else:
         db.user_limits.find_one_and_update({"user_telegram_id" : user_limits['user_telegram_id']}, { '$set': { limit_category : amount_value} }, return_document = ReturnDocument.AFTER)

def view_limits():
    user_history_obj = db.user_limits.find({'user_telegram_id' : user_limits['user_telegram_id']})
    for user_history in user_history_obj:
        if 'daily' in user_history and user_history['daily']:
            message = bot.send_message(user_limits['user_telegram_id'], 'Your Daily Limit is - {}'.format(user_history['daily']))
        if 'monthly' in user_history and user_history['monthly']:
            message = bot.send_message(user_limits['user_telegram_id'], 'Your Montly Limit is - {}'.format(user_history['monthly']))
        if 'yearly' in user_history and user_history['yearly']:
            message = bot.send_message(user_limits['user_telegram_id'], 'Your Yearly Limit is - {}'.format(user_history['yearly']))
	
	
#Handling /settle command
@bot.message_handler(commands=['settle'])
def command_settle(message):
    chat_id = message.chat.id
    message = bot.send_message(chat_id, "Please enter the date and time of the transaction you would like to settle in the following format, Eg: Sep 21 2022 1:33PM")
    bot.register_next_step_handler(message, settle_up)

def settle_up(message):
    record=dict()
    timestamp = datetime.strptime(message.text, timestamp_format)
    
    try:
        user_history = db.user_bills.find({'user_telegram_id' : message.chat.id})

        chat_id = message.chat.id
        if user_history is None:
            raise Exception("Sorry! No spending records found!")
        spend_total_str = "Here is your spending history : \n|    DATE AND TIME   | CATEGORY | AMOUNT | SHARED WITH  |\n-----------------------------------------------------------------------\n"
        for rec in user_history:
            # print(str(rec['timestamp'].strftime(timestamp_format)))
            # print(message.text)
            # print(type(rec))
            if(str(rec['timestamp'].strftime(timestamp_format))==message.text) :
                chat_id = message.chat.id
                record['_id']=rec['_id']
                record['timestamp']=rec['timestamp']
                record['cost']=rec['cost']
                record['number']=rec['number']
                record['category']=rec['category']
                record['shared_with']=rec['shared_with']
                spend_total_str += '{:20s} {:20s} {:20s} {}\n'.format(str(rec['number']), str(rec['timestamp'].strftime(timestamp_format)),  str(rec['category']),  str(rec['cost']), str(rec['shared_with'][0]) if 'shared_with' in rec.keys() else "")
        #bot.send_message(chat_id, spend_total_str)
        # print(record)
        
        bot.send_message(chat_id, 'The following expenditure has been selected to settle up: $' + str(record['cost']) + ' for ' + str(record['category']) + ' on ' + str(record['timestamp'].strftime(timestamp_format)))
        bot.send_message(chat_id, 'Your share of the expense is: {}'.format(record['cost']/(len(record['shared_with'])+1)))
        choice_for_settle(message, record)

    except Exception as e:
        bot.reply_to(message, "Oops!" + str(e) + str(e.__cause__) + str(e.__context__)) 


def choice_for_settle(message, record):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    markup.add("Yes")
    markup.add("No")
    bot.send_message(message.chat.id, 'Do you want to settle this bill?', reply_markup=markup)
    bot.register_next_step_handler(message, post_settle_selection,record)


def post_settle_selection(message,record):
    chat_id = message.chat.id
    response = message.text
    if response == "Yes":
        new_cost= record['cost']-(record['cost']/(len(record['shared_with'])+1))
        # print(new_cost)
        settled_user_bills= db.user_bills.find_one_and_update({"_id" : record['_id']}, { '$set': { "cost" : float(new_cost)} }, return_document = ReturnDocument.AFTER)
        paid_with_str = "Here is new expense you settled down : \n|    DATE AND TIME   | CATEGORY | AMOUNT TO BE PAID BY OTHERS | SHARED WITH | PAID BY \n-----------------------------------------------------------------------\n"
        paid_with_str += '{:20s} {:20s} {:20s} {:20s}  \n'.format(str(settled_user_bills['timestamp'].strftime(timestamp_format)),  str(settled_user_bills['category']),  str(settled_user_bills['cost']), str(settled_user_bills['shared_with']) ) 
        bot.send_message(chat_id, paid_with_str)
        
    else:
        bot.send_message(chat_id, "You did not select any expense to settle. ")

async def main():
    try:
        updater = Updater(api_token, use_context=True)
        dispatcher = updater.dispatcher

        main_conversation = ConversationHandler(
        entry_points=[
            CommandHandler('start', start_and_menu_command),
            CommandHandler('menu', start_and_menu_command),
            CommandHandler('add', command_add),
            CallbackQueryHandler(post_category_selection, pattern='^Food|Groceries|Utilities|Transport|Shopping|Miscellaneous|Others \(Please Specify\)|New_Category'),
            CommandHandler('edit', edit1),
            RegexHandler('^\$[0-9]+(\.[0-9][0-9])?$', post_amount_input),
            RegexHandler('^\"\"', post_category_selection)
        ],
        states={
        },
        fallbacks=[]
    )
        dispatcher.add_handler(main_conversation)
        updater.start_polling(drop_pending_updates=True)
        print("started")
        
        updater.idle()
        
    except Exception as e:
        print(str(e))
        time.sleep(3)
        # print(e)

if __name__ == '__main__':
    asyncio.run(main())
