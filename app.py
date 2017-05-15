from flask import Flask, jsonify
from scrape_web import *

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/tuko')
def tuko():
    return jsonify(get_tuko())


@app.route('/capital')
def capital():
    return jsonify(get_capital())


@app.route('/nation')
def nation():
    return jsonify(get_nation())


# @app.route('/the-star')
# def the_star():
#     return jsonify(get_the_star())


@app.route('/standard')
def standard():
    return jsonify(get_standard())


@app.route('/latest-news')
def latest_news():
    return jsonify(get_news())


if __name__ == '__main__':
    app.run()
