import os
from bottle import route, run, get, error, post, request
from pymongo import MongoClient
from dotenv import load_dotenv
import dns
import json
import pymongo
from bson.json_util import dumps
from textblob import TextBlob
import regex as re
from sklearn.metrics.pairwise import cosine_similarity as distance
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from bottle import get, run
import numpy as np

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
        text+=e['text']+' '
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


@route('/data')
def data():
    return dumps(coll.find())

@post('/document/create')
def newDocumentUser():
    #posts new user, message and iduser
    name = str(request.forms.get("userName"))
    text=str(request.forms.get('text'))
    chat=int(request.forms.get('idChat'))
    new_id = max(coll.distinct("idUser")) + 1
    new_id_message=max(coll.distinct("idMessage"))+1

    new_document = {
        "idUser": new_id,
        "userName": name,
        "idMessage":new_id_message,
        "idChat":chat,
        "text":text
    }

    coll.insert_one(new_document)

    print(f"Message added to collection with id {new_id_message} in chat {chat}")
    return new_document['text']


def getting_every_sentence():
    #gets a dictionary of users as keys and their sentences as values
    x=list(coll.find())
    users_dict=dict()
    for i in range(len(x)):
        if x[i]['userName'] not in users_dict:
            users_dict[x[i]['userName']]=x[i]['text']
        else:
            users_dict[x[i]['userName']]+=' ' +x[i]['text']
    for e in users_dict:
        users_dict[e]=re.sub(r"[^a-zA-Z0-9]+", ' ', users_dict[e])
    return users_dict

def getting_sparse_matrix():
    #gets the sparse matrix using the dictionary obtained in the previous function
    count_vectorizer = CountVectorizer(stop_words='english')
    sparse_matrix = count_vectorizer.fit_transform(getting_every_sentence().values())
    return sparse_matrix

@get('/recommendation/user=<user>')
def recommending_user(user):
    #returns a recommendation for user to talk to
    recommendation_dict=dict()
    count_vectorizer=CountVectorizer(stop_words='english')
    sparse_matrix = count_vectorizer.fit_transform(getting_every_sentence().values())
    doc_term_matrix = getting_sparse_matrix().todense()
    df = pd.DataFrame(doc_term_matrix, columns=count_vectorizer.get_feature_names(), index=getting_every_sentence().keys())
    similarity_matrix = distance(df, df)
    sim_df = pd.DataFrame(similarity_matrix, columns=getting_every_sentence().keys(), index=getting_every_sentence().keys())
    np.fill_diagonal(sim_df.values, 0)
    final_matrix=sim_df.idxmax()
    recommendation_dict[user]=final_matrix.loc[user]
    return recommendation_dict

@error(404)
def error404(error):
    return {'error': 'oops'}


port = int(os.getenv("PORT", 8080))
print(f"Running server {port}....")


run(host='127.0.0.1', port=8080)