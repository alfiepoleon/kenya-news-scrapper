from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# Set mongo url as environment var locally
# os.environ['MongoDB_URI'] = 'mongodb://localhost/kenya-news'

# Configure the connection to the database
client = MongoClient(os.environ['MongoDB_URI'])
# client = MongoClient('localhost', 27017)
db = client['kenya-news']  # Select the database
news_collection = db.news

"""
Api end points you can use with your server

Added skip in url so it can be passed to mongo query
So the request can have a skip parameter if it's requesting more than the 30 limited in 1st response
"""


@app.route('/')
def hello_world():
    return 'Hello World!'


'''
    News Start
'''


@app.route('/news/tuko', defaults={'skip': 0})
@app.route('/news/tuko/<int:skip>')
def tuko_news(skip):
    tuko_docs = [doc for doc in news_collection.find({
        'source': 'tuko'}, {'_id': 0}).skip(skip).limit(30).sort('date', -1)]
    return jsonify(tuko_docs)


@app.route('/news/capital', defaults={'skip': 0})
@app.route('/news/capital/<int:skip>')
def capital_news(skip):
    capital_docs = [doc for doc in news_collection.find({
        'source': 'capital'}, {'_id': 0}).skip(skip).limit(30).sort('date', -1)]
    return jsonify(capital_docs)


@app.route('/news/nation', defaults={'skip': 0})
@app.route('/news/nation/<int:skip>')
def nation_news(skip):
    nation_docs = [doc for doc in news_collection.find({
        'source': 'nation'}, {'_id': 0}).skip(skip).limit(30).sort('date', -1)]
    return jsonify(nation_docs)


@app.route('/news/the-star', defaults={'skip': 0})
@app.route('/news/the-star/<int:skip>')
def the_star_news(skip):
    the_star_docs = [doc for doc in news_collection.find({
        'source': 'the_star'}, {'_id': 0}).skip(skip).limit(30).sort('date', -1)]
    return jsonify(the_star_docs)


@app.route('/news/standard', defaults={'skip': 0})
@app.route('/news/standard/<int:skip>')
def standard_news(skip):
    standard_docs = [doc for doc in news_collection.find({
        'source': 'standard'}, {'_id': 0}).skip(skip).limit(30).sort('date', -1)]
    return jsonify(standard_docs)


@app.route('/latest-news/', defaults={'skip': 0})
@app.route('/latest-news/<int:skip>')
def latest_news(skip):
    news = [doc for doc in news_collection.find({}, {'_id': 0}).skip(skip).limit(30).sort('date', -1)]
    return jsonify(news)


'''
    News END
'''


if __name__ == '__main__':
    app.run()
