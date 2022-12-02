from flask import Flask, request
import json
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify
import os
from pymongo import MongoClient
from bson.json_util import dumps
from telebot import types
from datetime import datetime, date, timedelta
from telethon import TelegramClient
from dotenv import load_dotenv
from tabulate import tabulate
from datetime import datetime

from pymongo import MongoClient, ReturnDocument

load_dotenv()

api_token = os.getenv('TELEGRAM_BOT_TOKEN')
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
api_username = os.getenv('TELEGRAM_USERNAME')
cluster = os.getenv('MONGO_DB_URL')

mongo_client = MongoClient(cluster)
db = mongo_client.smartSpendDB
app = Flask(__name__)
api = Api(app)
CORS(app)


@app.route('/id/<id>')
def get_records_by_id(id):
   return dumps(list(db['user_bills'].find({'user_telegram_id': int(id)})))

@app.route('/tests', methods=['POST'])
def my_test_endpoint():
    print(request.get_json());
    
    date = datetime.now()
    print(date)
    db.user_bills.insert_one(request.get_json());
    return {'success': 'true'}
    
    # return jsonify(request.get_json())

@app.route("/")
def getAllExpenses():
    # return jsonify({'text':'Hello World!'})
    # return jsonify(db.user_bills);
    # print(cluster)
    # print("hi")
    result  = db.user_bills.find({'user_telegram_id': 5414346228})
    # print("hello")
    for rec in result: 
        print(rec['category'])
        # print(rec)

    # user_history = db.user_bills.find({'user_telegram_id' : 5414346228})
    # for rec in user_history:
        print(rec)

    print(result)
    for row in result:
        print(row)
    print(db['user_bills'].find({}).explain().get("executionStats", {}).get("nReturned"))
    print(db.user_bills.find({}))
    return dumps(list(db['user_bills'].find({})))
    # return jsonify({'text':'Hello World!'})

@app.route("/limits/<id>")
def getLimitsForUser(id):
   return dumps(list(db['user_limits'].find({'user_telegram_id': int(id)})));

if __name__ == '__main__':
   app.run(port=5002)