from flask_script import Manager
from app import app
from scrape_web import get_news
from datetime import datetime, timedelta
from pymongo import MongoClient
import os

manager = Manager(app)


@manager.command
def scrape_news():
    get_news()


@manager.command
def delete_old_news():
    """
        Deletes news older than 48 hours from the database
    """
    # Configure the connection to the database
    client = MongoClient(os.environ['MongoDB_URI'])
    # client = MongoClient('localhost', 27017)
    db = client['kenya-news']  # Select the database
    collection = db.news
    time_boundary = datetime.now() - timedelta(hours=48)
    print(time_boundary.isoformat())
    collection.remove({'$or': [
        {'date': {'$lt': time_boundary.isoformat()}},
        {'date': {'$eq': 0}}
    ]})


if __name__ == "__main__":
    manager.run()
