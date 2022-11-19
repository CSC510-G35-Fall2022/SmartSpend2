#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import telebot
from telebot import types
from datetime import datetime, date, timedelta
from telethon import TelegramClient
from pymongo import MongoClient, ReturnDocument
import os
from dotenv import load_dotenv
from tabulate import tabulate
load_dotenv()

from telegram.ext import CallbackContext
from telegram import Update

api_token = os.getenv('TELEGRAM_BOT_TOKEN')

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

#defines how the /start and /help commands have to be handled/processed
@bot.message_handler(commands=['start', 'menu'])
def start_and_menu_command(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    # print(cluster)
   
    text_intro = "Welcome to SmartSpend - a simple solution to spend money smartly on your expenses! \nHere is a list of available commands, please enter a command of your choice so that I can assist you further: \n\n"
    for c in commands:  # generate help text out of the commands dictionary defined at the top
        text_intro += "/" + c + ": "
        text_intro += commands[c] + "\n\n"
    bot.send_message(chat_id, text_intro)
    return True