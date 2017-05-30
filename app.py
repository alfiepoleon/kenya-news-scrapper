from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# Set mongo url as environment var
os.environ['MongoDB_URI'] = 'mongodb://localhost/kenya-news'

# Configure the connection to the database
client = MongoClient(os.environ['MongoDB_URI'])
# client = MongoClient('localhost', 27017)
db = client['kenya-news']  # Select the database
news_collection = db.news
ent_collection = db.ent
business_collection = db.business

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

'''
    Entertainment Start
'''


@app.route('/entertainment/tuko', defaults={'skip': 0})
@app.route('/entertainment/tuko/<int:skip>')
def tuko_ent(skip):
    docs = [doc for doc in ent_collection.find({
        'source': 'tuko'}, {'_id': 0}).skip(skip).limit(30).sort('date', -1)]
    return jsonify(docs)


@app.route('/entertainment/ghafla', defaults={'skip': 0})
@app.route('/entertainment/ghafla/<int:skip>')
def ghafla_ent(skip):
    docs = [doc for doc in ent_collection.find({
        'source': 'ghafla'}, {'_id': 0}).skip(skip).limit(30).sort('date', -1)]
    return jsonify(docs)


@app.route('/entertainment/sde', defaults={'skip': 0})
@app.route('/entertainment/sde/<int:skip>')
def sde_ent(skip):
    docs = [doc for doc in ent_collection.find({
        'source': 'sde'}, {'_id': 0}).skip(skip).limit(30).sort('date', -1)]
    return jsonify(docs)


@app.route('/entertainment/mpasho', defaults={'skip': 0})
@app.route('/entertainment/mpasho/<int:skip>')
def mpasho_ent(skip):
    docs = [doc for doc in ent_collection.find({
        'source': 'mpasho'}, {'_id': 0}).skip(skip).limit(30).sort('date', -1)]
    return jsonify(docs)


@app.route('/latest-entertainment/', defaults={'skip': 0})
@app.route('/latest-entertainment/<int:skip>')
def latest_ent(skip):
    ent = [doc for doc in ent_collection.find({}, {'_id': 0}).skip(skip).limit(30).sort('date', -1)]
    return jsonify(ent)


'''
    Entertainment END
'''

'''
    Business Start
'''


@app.route('/business/capital', defaults={'skip': 0})
@app.route('/business/capital/<int:skip>')
def capital_business(skip):
    capital_docs = [doc for doc in business_collection.find({
        'source': 'capital'}, {'_id': 0}).skip(skip).limit(30).sort('date', -1)]
    return jsonify(capital_docs)


@app.route('/business/nation', defaults={'skip': 0})
@app.route('/business/nation/<int:skip>')
def nation_business(skip):
    nation_docs = [doc for doc in business_collection.find({
        'source': 'nation'}, {'_id': 0}).skip(skip).limit(30).sort('date', -1)]
    return jsonify(nation_docs)


@app.route('/business/the-star', defaults={'skip': 0})
@app.route('/business/the-star/<int:skip>')
def the_star_business(skip):
    the_star_docs = [doc for doc in business_collection.find({
        'source': 'star'}, {'_id': 0}).skip(skip).limit(30).sort('date', -1)]
    return jsonify(the_star_docs)


@app.route('/business/standard', defaults={'skip': 0})
@app.route('/business/standard/<int:skip>')
def standard(skip):
    standard_docs = [doc for doc in business_collection.find({
        'source': 'standard'}, {'_id': 0}).skip(skip).limit(30).sort('date', -1)]
    return jsonify(standard_docs)


@app.route('/business/business-daily', defaults={'skip': 0})
@app.route('/business/business-daily/<int:skip>')
def business_daily_business(skip):
    docs = [doc for doc in business_collection.find({
        'source': 'business_daily'}, {'_id': 0}).skip(skip).limit(30).sort('date', -1)]
    return jsonify(docs)


@app.route('/business/kenyan-wall-street', defaults={'skip': 0})
@app.route('/business/kenyan-wall-street/<int:skip>')
def kenyan_wall_street_business(skip):
    docs = [doc for doc in business_collection.find({
        'source': 'kenyan_wall_street'}, {'_id': 0}).skip(skip).limit(30).sort('date', -1)]
    return jsonify(docs)


@app.route('/latest-business/', defaults={'skip': 0})
@app.route('/latest-business/<int:skip>')
def latest_business(skip):
    business = [doc for doc in business_collection.find({}, {'_id': 0}).skip(skip).limit(30).sort('date', -1)]
    return jsonify(business)


'''
    Business END
'''

if __name__ == '__main__':
    app.run()
