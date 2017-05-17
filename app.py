from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# Configure the connection to the database
client = MongoClient(os.environ['MongoDB_URI'])
# client = MongoClient('localhost', 27017)
db = client['kenya-news']  # Select the database
collection = db.news


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/tuko')
def tuko():
    tuko_docs = [doc for doc in collection.find({'source': 'tuko'}, {'_id': 0}).sort('date', -1)]
    return jsonify(tuko_docs)


@app.route('/capital')
def capital():
    capital_docs = [doc for doc in collection.find({'source': 'capital'}, {'_id': 0}).sort('date', -1)]
    return jsonify(capital_docs)


@app.route('/nation')
def nation():
    nation_docs = [doc for doc in collection.find({'source': 'nation'}, {'_id': 0}).sort('date', -1)]
    return jsonify(nation_docs)


# @app.route('/the-star')
# def the_star():
#     the_star_docs = [doc for doc in collection.find({'source': 'the_star'}, {'_id': 0}).sort('date', -1)]
#     return jsonify(the_star_docs)


@app.route('/standard')
def standard():
    standard_docs = [doc for doc in collection.find({'source': 'standard'}, {'_id': 0}).sort('date', -1)]
    return jsonify(standard_docs)


@app.route('/latest-news')
def latest_news():
    news = [doc for doc in collection.find({}, {'_id': 0}).sort('date', -1)]
    return jsonify(news)


if __name__ == '__main__':
    app.run()
