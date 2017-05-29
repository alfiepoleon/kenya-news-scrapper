import json
import requests
from requests.exceptions import ConnectionError, Timeout, HTTPError, TooManyRedirects
from bs4 import BeautifulSoup, SoupStrainer
from pymongo import MongoClient
import datetime
import dateutil.parser
from pytz import timezone
import os
import sys

"""
This is used by flask, returns json, example:
{
    "_id" : ObjectId("5927ed7e699a164e8d6de4bd"),
    "source" : "star",
    "title" : "Uhuru leaves for Italy, to attend G7 summit",
    "link" : "http://www.the-star.co.ke/news/2017/05/26/uhuru-leaves-for-italy-to-attend-g7-summit_c1568487",
    "image" : "http://www.the-star.co.ke/sites/default/files/styles/open_graph/public/1568495.jpg?itok=4cqU6c1h",
    "content" : [
        "President Uhuru Kenyatta has travelled to Taormina, Italy, for the 43rd G7 summit.",
        "The plane carrying Uhuru and his entourage departed Jomo Kenyatta International Airport shortly before 7:00 am on Friday."
    ],
    "date" : "2017-05-26T10:19:11+03:00",
    "date_added" : ISODate("2017-05-26T08:55:26.724Z")
}
"""
today = datetime.date.today()
localtz = timezone('Africa/Nairobi')

# Configure the connection to the database
# client = MongoClient(os.environ['MongoDB_URI'])
client = MongoClient('localhost', 27017)
db = client['kenya-news']  # Select the database
collection = db.ent

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}


def check_connection(url):
    try:
        request = requests.head(url)
        if request.status_code == 200:
            print('Connection ok...')
        else:
            print('Connection err')
    except (ConnectionError, Timeout):
        print('{} can not be reached, check your connection and retry later'.format(url))
        sys.exit(1)
    except (HTTPError, TooManyRedirects):
        print('There is an issue with the url, {}, confirm it, or retry later'.format(url))
        sys.exit(1)


def get_tuko():
    tuko_url = 'https://www.tuko.co.ke/'
    check_connection(tuko_url)
    tuko = requests.get('https://www.tuko.co.ke/arts-and-entertainment')
    soup = BeautifulSoup(tuko.text, 'lxml', parse_only=SoupStrainer('a'))
    tuko = []
    for link in soup.select('a.news__link', limit=10):
        news_title = '{}({})'.format(link.get_text(), link.get('href'))
        print(news_title)
        tuko_link = requests.get(link.get('href'))
        soup_link = BeautifulSoup(tuko_link.text, 'lxml', parse_only=SoupStrainer(['p', 'meta', 'img']))
        article_date = ''
        try:
            article_date = soup_link.find("meta", itemprop="datePublished")['content']
        except (TypeError, ValueError):
            print('Tuko: No article date meta')
            continue
        image = ''
        try:
            image = soup_link.find("meta", property="og:image")['content']
        except (TypeError, ValueError):
            try:
                image = soup_link.find('img', class_='article-image__picture')['src']
            except (TypeError, ValueError):
                print('Tuko: No image found')
        news_dict = {
            'source': 'tuko',
            'title': link.get_text(),
            'link': link.get('href'),
            'image': image,
            'content': [link_inner.get_text().strip(' ,.-') for link_inner in
                        soup_link.select('p.align-left > strong', limit=3) if not
                        link_inner.get_text().startswith('READ ALSO')],
            'date': article_date,
            'date_added': datetime.datetime.utcnow()
        }
        collection.update({'link': link.get('href')}, news_dict, upsert=True)
        tuko.append(news_dict)
    return tuko


def get_ghafla():
    ghafla_url = 'http://www.ghafla.com/ke/entertainment/'
    check_connection(ghafla_url)
    ghafla = requests.get(ghafla_url, headers=headers)
    print(ghafla)
    soup = BeautifulSoup(ghafla.text, 'lxml', parse_only=SoupStrainer('div'))
    ghafla = []
    for article in soup.select('div.omega', limit=10):
        article_link = article.a
        link = article_link['href']
        title = article_link.get_text()
        summary = article.p.get_text().strip()
        ghafla_link = requests.get(link)
        soup_link = BeautifulSoup(ghafla_link.text, 'lxml', parse_only=SoupStrainer('meta'))
        print(title, link)
        article_date = soup_link.find("meta", property="article:published_time")['content']
        image = ''
        try:
            image = soup_link.find("meta", property="og:image")['content']
        except (TypeError, ValueError):
            print('ghafla: No image found')

        news_dict = {
            'source': 'ghafla',
            'title': title,
            'link': link,
            'image': image,
            'content': [summary],
            'date': article_date,
            'date_added': datetime.datetime.utcnow()
        }
        collection.update({'link': link}, news_dict, upsert=True)
        ghafla.append(news_dict)
    return ghafla


def get_ent():
    get_tuko()
    get_ghafla()
