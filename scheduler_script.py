import os
from datetime import datetime, timedelta

from flask_script import Manager
from pymongo import MongoClient

from app import app
from news.scrape_cli import get_all_news as get_news_cli
from news.scrape_web import get_news

from entertainment.ent_cli import get_all_ent as get_ent_cli
from entertainment.ent_web import get_ent

manager = Manager(app)


@manager.command
def scrape_news():
    """
    Gets news from the web, then saves them in a database
    """
    get_news()


@manager.command
def news_cli():
    """
    Gets entertainment news from the web. But just displays in the cli, no databases involved
    """
    get_news_cli()


@manager.command
def ent_web():
    """
    Gets entertainment news from the web, then saves them in a database
    """
    get_ent()


@manager.command
def ent_cli():
    """
    Gets news from the web. But just displays in the cli, no databases involved
    """
    get_ent_cli()


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
