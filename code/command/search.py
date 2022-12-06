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
from pymongo import MongoClient
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

def command_select(message, bot):
    """Starts the search command"""
    chat_id = message.chat.id
   
    message = bot.send_message(chat_id, 'what is the product Name?')
    bot.register_next_step_handler(message, product_table, bot)
    

def product_table(message, bot):
    """Displays a product table from the internet showing prices and comparisons"""
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