import os
from pymongo import MongoClient
from dotenv import load_dotenv
import dns
from bson.json_util import dumps, loads
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

def getting_every_sentence():
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
    count_vectorizer = CountVectorizer(stop_words='english')
    sparse_matrix = count_vectorizer.fit_transform(getting_every_sentence().values())
    return sparse_matrix

@get('/recomendation/user=<user>')
def recommending_user(user):
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

port = int(os.getenv("PORT", 8080))
print(f"Running server {port}....")


run(host='127.0.0.1', port=8080)