from flask_script import Manager
from app import app
from scrape_web import get_news

manager = Manager(app)


@manager.command
def get_news():
    get_news()


if __name__ == "__main__":
    manager.run()
