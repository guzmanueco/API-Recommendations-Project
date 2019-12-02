import os
from bottle import route, run, get, error
from pymongo import MongoClient
from dotenv import load_dotenv
import dns
import json
import pymongo
from bson.json_util import dumps
from textblob import TextBlob






load_dotenv()
url=os.getenv('password')
client = MongoClient(url)
db = client['chat']
coll = db['chat-prueba']



@get("/")
def index():
    #return every document on the collection
    return dumps(coll.find())


@get("/conversation/chat=<x>/")
def getting_messages(x):
    #returns every document with idChat=x
    x=int(x)
    return dumps(coll.find({'idChat':x},{'idChat':1,'userName':1,'text':1}))

@get("/conversation/chat=<x>/user=<y>/")
def getting_x_user(x,y):
    #returns every document with idChat=x and user=y
    x=int(x)
    return dumps(coll.find({'idChat':x,'userName':y},{'idChat':1,'userName':1,'text':1}))

@get('/conversation/all_users/')
def return_allusers():
    #returns the list of users on everychat
    return dumps(coll.find({}).distinct('userName'))

@get("/conversation/chat=<x>/all_users/")
def return_users(x):
    #returns the list of users of chat with idChat=x
    x=int(x)
    return dumps(coll.find({'idChat':x}).distinct('userName'))

@get("/conversation/num_mess=<y>/")
def getting_x_messages(y):
    #returns y number of documents
    y=int(y)
    return dumps(coll.find({},{'idChat':1,'userName':1,'text':1}).limit(y))

@get("/conversation/chat=<x>/num_mess=<y>/")
def getting_x_messages_chat(x,y):
    #returns y number of documents with idChat=x
    x=int(x)
    y=int(y)
    return dumps(coll.find({'idChat':x},{'idChat':1,'userName':1,'text':1}).limit(y))

@get("/conversation/sentiment/aggregate/")
def sentiments():
    #returns polarity analysis of every message of every chat
    sentiment=dict()
    text=''
    for e in coll.find():
        text+=e['text']
    sentiment['analysis']=TextBlob(text).sentiment
    return sentiment

@get("/conversation/chat=<x>/sentiment/per-user/")
def sentiments_chat(x):
    #returns polarity of each user in chat=x
    x=int(x)
    sentiment=dict()
    text=''
    for e in coll.find({'idChat':x}):
        text+=e['text']
    sentiment['analysis']=TextBlob(text).sentiment
    return sentiment

@get("/conversation/sentiment/per-user/")
def sentiment_of_everyone():
    #returns a per user polarity analysis for every user in every chat
    conversation=dict()
    conv_analysis=dict()
    for e in coll.find():
        if e['userName'] not in conversation:
            conversation[e['userName']]=e['text']
        else:
            conversation[e['userName']]+=e['text']
    for e in conversation:
        conv_analysis[e]=TextBlob(conversation[e]).sentiment
    return conv_analysis

@get("/conversation/chat=<x>/sentiment/per-user/")
def sentiment_of_everyone_chat(x):
    #returns a polarity analysis of each user on chat=x
    x=int(x)
    conversation=dict()
    conv_analysis=dict()
    for e in coll.find({'idChat':x}):
        if e['userName'] not in conversation:
            conversation[e['userName']]=e['text']
        else:
            conversation[e['userName']]+=e['text']
    for e in conversation:
        conv_analysis[e]=TextBlob(conversation[e]).sentiment
    return conv_analysis


@get('/conversation/user=<user>/sentiment/')
def sentiment_user(user):
    #returns the aggregate polarity analysis for every sentence of a user=y on every chat
    conversation=dict()
    conv_analysis=dict()
    for e in coll.find():
        if e['userName']==user:
            conversation[user]=e['text']
        else:
            conversation[user]+=e['text']
    conv_analysis[user]=TextBlob(conversation[user]).sentiment
    return conv_analysis


@get('/conversation/chat=<x>/user=<user>/sentiment/')
def sentiment_user_chat(x,user):
    #returns the polarity analysis of a user=user on chat=x
    x=int(x)
    conversation=dict()
    conv_analysis=dict()
    for e in coll.find({'idChat':x}):
        if e['userName']==user:
            conversation[user]=e['text']
        else:
            conversation[user]+=e['text']
    conv_analysis[user]=TextBlob(conversation[user]).sentiment
    return conv_analysis

@error(404)
def error404(error):
    return {'error': 'oops'}


port = int(os.getenv("PORT", 8080))
print(f"Running server {port}....")


run(host='127.0.0.1', port=8080)