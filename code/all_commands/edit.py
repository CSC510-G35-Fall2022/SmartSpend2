
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

#function to edit date, category or cost of a transaction
@bot.message_handler(commands=['edit'])
def edit1(update: Update, context: CallbackContext):
    # info = bot.reply_to(m, "Please enter the date and time of the transaction you made in the following format, Eg: Sep 21 2022 1:33PM")
  #show show_history
    chat_id = update.effective_chat.id
    user_history = db.user_bills.find({'user_telegram_id' :  chat_id})
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
    number = bot.reply_to(update.effective_message, "Please type the transaction number you want to edit")
    # print(number)
    bot.register_next_step_handler(number, edit3(update))

def edit3(update):
    global user_bills
    chat_id = update.effective_chat.id
    user_history = list(db.user_bills.find({'user_telegram_id' :chat_id, 'number': int(m.text)}))

    if len(list(user_history)) == 0:
        
        bot.reply_to(update.effective_message, 'No data found.')
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row_width = 2
        choices = ['Date & Time','Category','Cost']
        for c in choices:
            markup.add(c)
        bot.send_message(chat_id, 'Here are the details of your transaction: \n\nDate & Time: {}\nCategory: {}\nCost: ${}'.format(user_history[0]['timestamp'], user_history[0]['category'], user_history[0]['cost']))
        
        choice = bot.send_message(chat_id, "What do you want to update?", reply_markup = markup)
        user_bills = user_history[0]
        bot.register_next_step_handler(choice, edit4(update))

def edit4(update: Update):

    choice1 = update.effective_message.text
    chat_id = update.effective_chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    for cat in spend_categories:
        markup.add(cat)
    
    if(choice1 == 'Date & Time'):
        new_date = bot.reply_to(update.effective_message, "Please enter the new date in format, Eg: Sep 21 2022 1:33PM")
        bot.register_next_step_handler(new_date, edit_date(update))
        
    if(choice1 == 'Category'):
        new_cat = bot.reply_to(update.effective_message, "Please select the new category", reply_markup = markup)
        # print("category", new_cat)
        bot.register_next_step_handler(new_cat, edit_cat(update))
        
                
    if(choice1 == 'Cost'):
        new_cost = bot.reply_to(chat_id, "Please type the new cost")
        # print(new_cost)
        bot.register_next_step_handler(new_cost, edit_cost(update))        

def edit_date(update: Update):
    global user_bills
    chat_id = update.effective_chat.id
    timestamp = datetime.strptime(m.text, timestamp_format)
    user_bills = db.user_bills.find_one_and_update({"_id" : user_bills['_id']}, { '$set': { "timestamp" : timestamp} }, return_document = ReturnDocument.AFTER)
    bot.reply_to(update.effective_message, "Date is updated")
    #print(user_bills)
    # print(user_bills['shared_with'])
    if user_bills['shared_with'] != 'NULL':
        for x in user_bills['shared_with']:
            # print(x)
            spend_total_str = "Here is the modified expense : \n|    DATE AND TIME   | CATEGORY | AMOUNT \n-----------------------------------------------------------------------\n"
            spend_total_str += '{:20s} {:20s} {:20s} \n'.format(str(user_bills['timestamp'].strftime(timestamp_format)),  str(user_bills['category']),  str(user_bills['cost'])) 
            try:
                asyncio.run(updating_user_with_updated_expense(update.edited_message, x, user_bills))
            except:
                time.sleep(5)
            bot.send_message(user_bills['user_telegram_id'], spend_total_str)
	
    # print('Updated record '+ str(user_bills) +' to user_bills collection')
    
def edit_cat(update: Update):
    global user_bills
    # print(user_bills)
    category = m.text
    if category == 'Others (Please Specify)':
        message = bot.reply_to(update.effective_message, 'Please type new category.')
        bot.register_next_step_handler(update.effective_message, edit_cat)
    else:
        updated_user_bill=db.user_bills.find_one_and_update({"_id" : user_bills['_id']}, { '$set': { "category" : category} }, return_document = ReturnDocument.AFTER)
        bot.reply_to(update.effective_message, "Category is updated")
        # print(user_bills['shared_with'])
        if updated_user_bill['shared_with']:
            for x in updated_user_bill['shared_with']:
                # print("jere")
                # print(x)
                spend_total_str = "Here is the modified expense : \n|    DATE AND TIME   | CATEGORY | AMOUNT \n-----------------------------------------------------------------------\n"
                spend_total_str += '{:20s} {:20s} {:20s} \n'.format(str(updated_user_bill['timestamp'].strftime(timestamp_format)),  str(updated_user_bill['category']),  str(updated_user_bill['cost'])) 
                asyncio.run(updating_user_with_updated_expense(m, x, updated_user_bill))
                bot.send_message(user_bills['user_telegram_id'], spend_total_str)
		
        # print('Updated record '+ str(user_bills) +' to user_bills collection')

def edit_cost(update: Update):
    global user_bills
    new_cost = update.effective_message.text
    try:
        if(validate_entered_amount(new_cost) != 0):
            updated_user_bill=db.user_bills.find_one_and_update({"_id" : user_bills['_id']}, { '$set': { "cost" : float(new_cost)} }, return_document = ReturnDocument.AFTER)
            bot.reply_to(update.effective_chat.id, "Cost is updated")
	    #update the shared user 
            if updated_user_bill['shared_with'] != 'NULL':
                for x in updated_user_bill['shared_with']:
                    # print(x)
                    spend_total_str = "Here is the modified expense : \n|    DATE AND TIME   | CATEGORY | AMOUNT \n-----------------------------------------------------------------------\n"
                    spend_total_str += '{:20s} {:20s} {:20s} \n'.format(str(updated_user_bill['timestamp'].strftime(timestamp_format)),  str(updated_user_bill['category']),  str(updated_user_bill['cost'])) 
                    asyncio.run(updating_user_with_updated_expense(update.effective_message, x, updated_user_bill))
                    bot.send_message(user_bills['user_telegram_id'], spend_total_str)
            # print('Updated record '+ str(user_bills) +' to user_bills collection')
        else:
            bot.reply_to(update.effective_message, "The cost is invalid")
            return
    except Exception as e:
        bot.reply_to(m, "Oops!" + str(e) + str(e.__cause__) + str(e.__context__))
	

def validate_entered_amount(amount_entered):
    if len(amount_entered) > 0 and len(amount_entered) <= 15:
        if amount_entered.isdigit:
            if re.match("^[0-9]*\\.?[0-9]*$", amount_entered):
                amount = round(float(amount_entered), 2)
                if amount > 0:
                    return str(amount)
    return 0

# To send the shared users the updated expense
async def updating_user_with_updated_expense(message,user_name, user_bills):
    try:
        user = await find_user_by_username(user_name)

        if user == None:
            return

        bot.send_message(user.id, 'An expense has been modified.\n The new expense for {} on {} with value of {} was shared with you.'.format(str(user_bills['number']), str(user_bills['category']), str(user_bills['timestamp'].strftime(timestamp_format)), str(user_bills['cost'])))
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
