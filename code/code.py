
# -*- coding: utf-8 -*-
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
from telegram import ParseMode
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
spendlimit_categories = ['Food', 'Groceries', 'Utilities', 'Transport', 'Shopping', 'Miscellaneous', 'View Limits']
spend_display_option = ['Day', 'Month', 'All']
timestamp_format = '%b %d %Y %I:%M%p'
limit_categories = ['daily', 'monthly', 'yearly', 'View Limits']
delete_options = ['Delete All', 'Delete a specific record']

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
    'settle': 'Settle an expense shared with you',
    'limitcategory': 'Set Monthly limits for each spending categories',
    'website': 'Visit website to help you manage your expenses better'
}

bot = telebot.TeleBot(api_token)

telebot.logger.setLevel(logging.INFO)


# #Define listener for requests by user
# def listener(user_requests):
#     for req in user_requests:
#         if(req.content_type=='text'):
#             print("{} name: {} chat_id: {} message: {}".format(str(datetime.now()),str(req.chat.first_name),str(req.chat.id),str(req.text)))
           
#             # print("{} name: {} chat_id: {} message: {}".format(str(datetime.now()),str(req.chat.first_name),str(req.chat.id)))

# bot.set_update_listener(listener)

#defines how the /start and /help commands have to be handled/processed
@bot.message_handler(commands=['start', 'menu'])
def start_and_menu_command(m):
    chat_id = m.chat.id
    # print(cluster)
   
    text_intro = "Welcome to SmartSpend - a simple solution to spend money smartly on your expenses! \nHere is a list of available commands, please enter a command of your choice so that I can assist you further: \n\n"
    for c in commands:  # generate help text out of the commands dictionary defined at the top
        text_intro += "/" + c + ": "
        text_intro += commands[c] + "\n\n"
    bot.send_message(chat_id, text_intro)
    return True


#defines how the /start and /help commands have to be handled/processed
@bot.message_handler(commands=['website'])
def website_command(m):
    chat_id = m.chat.id
    # print(cluster)
    # print('https://localhost:4200/{}'.format(chat_id))
    url = 'https://localhost:4200/{}'.format(chat_id)
    bot.send_message(chat_id, text="Check out the website:\n http://localhost:4200/{}".format(chat_id),parse_mode=ParseMode.MARKDOWN)
    return True

#defines how the /new command has to be handled/processed
@bot.message_handler(commands=['add'])
def command_add(message):
    chat_id = message.chat.id
    user_bills['user_telegram_id'] = chat_id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    for c in spend_categories:
        markup.add(c)
    markup.add("Cancel")
    msg = bot.reply_to(message, 'Select Category \nSelect Cancel to abort.', reply_markup=markup)
    # print('category', message.text)
    bot.register_next_step_handler(msg, post_category_selection)
    
    
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
                    
def post_category_selection(message):
        # print(message.text)
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
                    bot.register_next_step_handler(message, post_amount_input)
                else:
                    msg = bot.send_message(chat_id, 'Invalid', reply_markup=types.ReplyKeyboardRemove())
                    raise Exception("Oh no! Sorry I don't recognise this category \"{}\"!".format(selected_category))
            elif str(selected_category) == 'Others (Please Specify)':
                spend_categories.append('New_Category')
                message = bot.send_message(chat_id, 'Please type new category.')
                bot.register_next_step_handler(message, post_category_selection)
            else:
                user_bills['category'] = selected_category
                message = bot.send_message(chat_id, 'How much did you spend on {}? \n(Enter numeric values only or Type Cancel to abort!)'.format(str(selected_category)))
                # print('message:', message)
                bot.register_next_step_handler(message, post_amount_input)
                # print(post_amount_input)
        except Exception as e:
            bot.reply_to(message,str(e))
            display_text = ""
            for c in commands:  # generate help text out of the commands dictionary defined at the top
                display_text += "/" + c + ": "
                display_text += commands[c] + "\n"
            bot.send_message(chat_id, 'Please select a menu option from below:')
            bot.send_message(chat_id, display_text)

def post_amount_input(message):
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

        get_sharing_details(message)

    except Exception as e:
        bot.reply_to(message,str(e))
        display_text = ""
        for c in commands:  # generate help text out of the commands dictionary defined at the top
            display_text += "/" + c + ": "
            display_text += commands[c] + "\n"
        bot.send_message(chat_id, 'Please select a menu option from below:')
        bot.send_message(chat_id, display_text)

def get_sharing_details(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 3
    markup.add("Yes")
    markup.add("No")
    markup.add("Cancel")
    bot.send_message(message.chat.id, 'Do you want to split this bill with any other users?', reply_markup=markup)
    bot.register_next_step_handler(message, post_sharing_selection)

def post_sharing_selection(message):
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
        bot.register_next_step_handler(message, handle_user_id_input_for_sharing)

    else:
        # handle direct commit scenario
        add_bill_to_database(message)

def handle_user_id_input_for_sharing(message):
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
        print(user_history)
        
        chat_id = message.chat.id
        if user_history is None:
            raise Exception("Sorry! No spending records found!")
        spend_total_str = "Here is your spending history : \n EXPENSE NUMBER |    DATE AND TIME   | CATEGORY | AMOUNT |\n-----------------------------------------------------------------------\n"
        
        cat=[]
        amt=[]
        hist_dict={}
        B=TelegramBot(api_token, chat_id)
        for rec in user_history:
            print(rec)
            cat.append(str(rec['category']))
            amt.append(float(rec['cost']))
            if str(rec['timestamp'].strftime(timestamp_format))[:3] in hist_dict:
                hist_dict[str(rec['timestamp'].strftime(timestamp_format))[:3]] += float(rec['cost'])
            else:
                hist_dict[str(rec['timestamp'].strftime(timestamp_format))[:3]] = float(rec['cost'])
            spend_total_str += '\n{:20s} {:20s} {:20s} {:20s}\n'.format(str(rec['number']), str(rec['timestamp'].strftime(timestamp_format)),  str(rec['category']),  str(rec['cost']))
            if 'shared_with' in rec.keys():
                spend_total_str += 'Shared With:'
                for username in rec['shared_with']:
                    spend_total_str += ' {}'.format(str(username))
                spend_total_str += '\n'
        
        plt.clf()
        month = list(hist_dict.keys())
        exp = list(hist_dict.values())
        plt.bar(range(len(hist_dict)),exp, tick_label=month)
        B.send_plot(plt)
        B.clean_tmp_dir()
        bot.send_message(chat_id, spend_total_str)
    except Exception as e:
        bot.reply_to(message, "Oops!" + str(e) + str(e.__cause__) + str(e.__context__))    
                

#function to edit date, category or cost of a transaction
@bot.message_handler(commands=['edit'])
def edit1(m):
    # info = bot.reply_to(m, "Please enter the date and time of the transaction you made in the following format, Eg: Sep 21 2022 1:33PM")
  #show show_history
    user_history = db.user_bills.find({'user_telegram_id' :  m.chat.id})
    chat_id = m.chat.id
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
    bot.send_message(m.chat.id, spend_total_str)
    number = bot.reply_to(m, "Please type the transaction number you want to edit")
    # print(number)
    bot.register_next_step_handler(number, edit3)

def edit2(m):
    try:
        global user_bills
        user_bills['number'] = m.text
        # print()
        # print(user_bills['number'])
        # print("number " + str(m.text))
        # user_bills['timestamp'] = datetime.strptime(m.text, timestamp_format)
        # print(user_bills['timestamp'])
        info = bot.reply_to(m, "Please enter the category of the transaction you made.")
        bot.register_next_step_handler(info, edit3)
    except Exception as e:
        if 'does not match format' in str(e):
            bot.reply_to(m, 'Date format is not correct. Please give /edit command again and enter the date and time in the format, Eg: Sep 21 2022 1:33PM')
        else:
            print(str(e))

def edit3(m):
    global user_bills
    # user_history = list(db.user_bills.find({'user_telegram_id' : m.chat.id, 'timestamp': {'$gte': user_bills['timestamp'], '$lt': user_bills['timestamp'] + timedelta(seconds=59)}, 'category': m.text}))
    user_history = list(db.user_bills.find({'user_telegram_id' : m.chat.id, 'number': int(m.text)}))

    if len(list(user_history)) == 0:
        
        bot.reply_to(m, 'No data found.')
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row_width = 2
        choices = ['Date & Time','Category','Cost']
        for c in choices:
            markup.add(c)
        bot.send_message(m.chat.id, 'Here are the details of your transaction: \n\nDate & Time: {}\nCategory: {}\nCost: ${}'.format(user_history[0]['timestamp'], user_history[0]['category'], user_history[0]['cost']))
        
        choice = bot.send_message(m.chat.id, "What do you want to update?", reply_markup = markup)
        user_bills = user_history[0]
        bot.register_next_step_handler(choice, edit4)

def edit4(m):
    choice1 = m.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    for cat in spend_categories:
        markup.add(cat)
    
    if(choice1 == 'Date & Time'):
        new_date = bot.reply_to(m, "Please enter the new date in format, Eg: Sep 21 2022 1:33PM")
        bot.register_next_step_handler(new_date, edit_date)
        
    if(choice1 == 'Category'):
        new_cat = bot.reply_to(m, "Please select the new category", reply_markup = markup)
        # print("category", new_cat)
        bot.register_next_step_handler(new_cat, edit_cat)
        
                
    if(choice1 == 'Cost'):
        new_cost = bot.reply_to(m, "Please type the new cost")
        # print(new_cost)
        bot.register_next_step_handler(new_cost, edit_cost)        

def edit_date(m):
    global user_bills
    timestamp = datetime.strptime(m.text, timestamp_format)
    user_bills = db.user_bills.find_one_and_update({"_id" : user_bills['_id']}, { '$set': { "timestamp" : timestamp} }, return_document = ReturnDocument.AFTER)
    bot.reply_to(m, "Date is updated")
    #print(user_bills)
    # print(user_bills['shared_with'])
    if user_bills['shared_with'] != 'NULL':
        for x in user_bills['shared_with']:
            # print(x)
            spend_total_str = "Here is the modified expense : \n|    DATE AND TIME   | CATEGORY | AMOUNT \n-----------------------------------------------------------------------\n"
            spend_total_str += '{:20s} {:20s} {:20s} \n'.format(str(user_bills['timestamp'].strftime(timestamp_format)),  str(user_bills['category']),  str(user_bills['cost'])) 
            try:
                asyncio.run(updating_user_with_updated_expense(m, x, user_bills))
            except:
                time.sleep(5)
            bot.send_message(user_bills['user_telegram_id'], spend_total_str)
    
    # print('Updated record '+ str(user_bills) +' to user_bills collection')
    
def edit_cat(m):
    global user_bills
    # print(user_bills)
    category = m.text
    if category == 'Others (Please Specify)':
        message = bot.reply_to(m, 'Please type new category.')
        bot.register_next_step_handler(message, edit_cat)
    else:
        updated_user_bill=db.user_bills.find_one_and_update({"_id" : user_bills['_id']}, { '$set': { "category" : category} }, return_document = ReturnDocument.AFTER)
        bot.reply_to(m, "Category is updated")
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

def edit_cost(m):
    global user_bills
    new_cost = m.text
    try:
        if(validate_entered_amount(new_cost) != 0):
            updated_user_bill=db.user_bills.find_one_and_update({"_id" : user_bills['_id']}, { '$set': { "cost" : float(new_cost)} }, return_document = ReturnDocument.AFTER)
            bot.reply_to(m, "Cost is updated")
        #update the shared user 
            if updated_user_bill['shared_with'] != 'NULL':
                for x in updated_user_bill['shared_with']:
                    # print(x)
                    spend_total_str = "Here is the modified expense : \n|    DATE AND TIME   | CATEGORY | AMOUNT \n-----------------------------------------------------------------------\n"
                    spend_total_str += '{:20s} {:20s} {:20s} \n'.format(str(updated_user_bill['timestamp'].strftime(timestamp_format)),  str(updated_user_bill['category']),  str(updated_user_bill['cost'])) 
                    asyncio.run(updating_user_with_updated_expense(m, x, updated_user_bill))
                    bot.send_message(user_bills['user_telegram_id'], spend_total_str)
            # print('Updated record '+ str(user_bills) +' to user_bills collection')
        else:
            bot.reply_to(m, "The cost is invalid")
            return
    except Exception as e:
        bot.reply_to(m, "Oops!" + str(e) + str(e.__cause__) + str(e.__context__))
    
    
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
            raise Exception("Sorry I can't show spendings for \"{}\"!".format(display_option))

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
        cat=[]
        amt=[]
        for record in records:
            total_text += '{:25s} {}\n'.format(record['_id']['category'],  str(record['count']))
            cat.append(record['_id']['category'])
            amt.append(float(record['count']))

        spending_text = ""
        if len(total_text) == 0:
            spending_text = "You have no spendings for {}!".format(display_option)
        else:
            spending_text = "Here are your {} total spendings:\n | CATEGORIES | AMOUNT |\n----------------------------------------\n{}".format(display_option.lower(), total_text)

        bot.send_message(chat_id, spending_text)
        amt_per=[]
        s=sum(amt)
        for i in amt:
            amt_per.append((i/s)*100)
        B=TelegramBot(api_token, chat_id)
        plt.clf()
        plt.pie(amt_per, labels=cat, shadow=True, autopct='%1.1f%%')
        B.send_plot(plt)
        B.clean_tmp_dir()
    except Exception as e:
        bot.reply_to(message, str(e) + str(e.__cause__))

#handles "/delete" command
@bot.message_handler(commands=['delete'])
def command_delete(message):

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 2
    for c in delete_options:
        markup.add(c)
    # markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    # markup.row_width = 2
    # options = ["Delete all", "Delete a specific transaction"]
    # for mode in options:
    #     markup.add(mode)
    # db.user_bills.delete_many({'user_telegram_id': message.chat.id})
    msg = bot.send_message(message.chat.id, 'Would you like to delete all data or a specific expense?', reply_markup=markup)

    bot.register_next_step_handler(msg, post_delete_selection)

    # # msg = bot.send_message(message.chat.id, 'Would you like to delete all data or a specific expense?', reply_markup=markup)
    # print("Message: "  + msg.text)
    # if (msg.text ==delete_options[0]):
    #     print('delete all')

    #     # db.user_bills.delete_many({'user_telegram_id': message.chat.id})
    #     db.user_bills.delete_many({})
    #     bot.send_message(message.chat.id, 'All data deleted.')
    # elif (msg == delete_options[1]):
    #     print('delete one')
    #     num = bot.send_message(message.chat.id, "which transaction number would you like to delete")
    #     user_history = db.user_bills.find({'user_telegram_id' : message.chat.id, 'number': 2})

def post_delete_selection(message):
        # print(message.text)
        try:
            chat_id = message.chat.id
            selected_delete_option = message.text

            if (selected_delete_option ==delete_options[0]):
                print('delete all')

                db.user_bills.delete_many({'user_telegram_id': message.chat.id})
                # db.user_bills.delete_many({})
                bot.send_message(message.chat.id, 'All data deleted.')
            elif (selected_delete_option == delete_options[1]):
                print('delete one')
                num = bot.send_message(message.chat.id, "which transaction number would you like to delete")
                bot.register_next_step_handler(num, delete_one_handler)
                user_history = db.user_bills.find({'user_telegram_id' : message.chat.id, 'number': 2})
        except Exception as e:
            bot.reply_to(message, 'Oh no! ' + str(e))
            display_text = ""
            for c in commands:  # generate help text out of the commands dictionary defined at the top
                display_text += "/" + c + ": "
                display_text += commands[c] + "\n"
            bot.send_message(chat_id, 'Please select a menu option from below:')
            bot.send_message(chat_id, display_text)

def delete_one_handler(message):
    chat_id = message.chat.id
    record_to_delete = message.text
    print(record_to_delete)
    try:
        db.user_bills.delete_one({'number': int(record_to_delete)})
        bot.send_message(message.chat.id, 'Deleted record successfully')
    except Exception as e:
        bot.reply_to(message, 'Oh no! ' + str(e))


    # if selected_limit_category != 'View Limits' and selected_limit_category in limit_categories:
    #     global limit_category
    #     limit_category = selected_limit_category
    #     message = bot.send_message(chat_id, 'How much limit do you want to set on a {} basis? \n(Enter numeric values only)'.format(str(limit_category)))
    #     bot.register_next_step_handler(message, post_limit_amount_input)
    # elif selected_limit_category == 'View Limits':
    #     # print("viewing limits for current user")
    #     view_limits()
    # else:
    #     message = bot.send_message(chat_id, 'Entered wrong input')

    

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
        message = bot.send_message(chat_id, 'How much limit do you want to set for {} category? \n(Enter numeric values only)'.format(str(spend_category)))
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

    user_history = list(db.user_limits.find({'user_telegram_id' : user_limits['user_telegram_id']}))

    if len(user_history) == 0:
        user_limits[spend_category] = amount_value
        db.user_limits.insert_one(user_limits)
        print('Added Spend Category Limit record '+ str(user_limits) +' to user_limits collection')
        message = bot.send_message(chat_id, 'Added Limit for '+ spend_category+": "+ str(amount_value))
    else:
        db.user_limits.find_one_and_update({"user_telegram_id" : user_limits['user_telegram_id']}, { '$set': { spend_category : amount_value} }, return_document = ReturnDocument.AFTER)
        print('Updated Spend Category Limit record '+ str(user_limits) +' to user_limits collection')
        message = bot.send_message(chat_id, 'Updated Limit for '+ spend_category+": "+ str(amount_value))

def view_spendlimits():
    user_history_obj = db.user_limits.find({'user_telegram_id' : user_limits['user_telegram_id']})
    for user_history in user_history_obj:
        if 'Food' in user_history and user_history['Food']:
            message = bot.send_message(user_limits['user_telegram_id'], 'Your Food Limit is - {}'.format(user_history['Food']))
        if 'Groceries' in user_history and user_history['Groceries']:
            message = bot.send_message(user_limits['user_telegram_id'], 'Your Groceries Limit is - {}'.format(user_history['Groceries']))
        if 'Utilities' in user_history and user_history['Utilities']:
            message = bot.send_message(user_limits['user_telegram_id'], 'Your Utilities Limit is - {}'.format(user_history['Utilities']))
        if 'Transport' in user_history and user_history['Transport']:
            message = bot.send_message(user_limits['user_telegram_id'], 'Your Transport Limit is - {}'.format(user_history['Transport']))
        if 'Shopping' in user_history and user_history['Shopping']:
            message = bot.send_message(user_limits['user_telegram_id'], 'Your Shopping Limit is - {}'.format(user_history['Shopping']))
        if 'Miscellaneous' in user_history and user_history['Miscellaneous']:
            message = bot.send_message(user_limits['user_telegram_id'], 'Your Miscellaneous Limit is - {}'.format(user_history['Miscellaneous']))



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
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(3)
       

if __name__ == '__main__':
    asyncio.run(main())
