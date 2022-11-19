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

@app.route("/")
def hello():
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

class Employees(Resource):
    def get(self):
        return {'employees': [{'id':1, 'name':'Balram'},{'id':2, 'name':'Tom'}]} 

class Employees_Name(Resource):
    def get(self, employee_id):
        print('Employee id:' + employee_id)
        result = {'data': {'id':1, 'name':'Balram'}}
        return jsonify(result)       


api.add_resource(Employees, '/employees') # Route_1
api.add_resource(Employees_Name, '/employees/<employee_id>') # Route_3


if __name__ == '__main__':
   app.run(port=5002)