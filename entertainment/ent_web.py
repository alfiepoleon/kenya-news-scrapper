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
from check_connection import check_connection

"""
This is used by flask, returns json, example:

"""
today = datetime.date.today()
localtz = timezone('Africa/Nairobi')

# Configure the connection to the database
client = MongoClient(os.environ['MongoDB_URI'])
db = client['kenya-news']  # Select the database
collection = db.ent

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}


def get_tuko():
    tuko_url = 'https://www.tuko.co.ke/'
    if check_connection(tuko_url):
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
                'category': 'entertainment',
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
    if check_connection(ghafla_url):
        ghafla = requests.get(ghafla_url, headers=headers)
        soup = BeautifulSoup(ghafla.text, 'lxml', parse_only=SoupStrainer('div'))
        ghafla = []
        for article in soup.select('div.omega', limit=10):
            article_link = article.a
            link = article_link['href']
            title = article_link.get_text()
            summary = article.p.get_text().strip()
            ghafla_link = requests.get(link)
            soup_link = BeautifulSoup(ghafla_link.text, 'lxml', parse_only=SoupStrainer('meta'))
            article_date = soup_link.find("meta", property="article:published_time")['content']
            image = ''
            try:
                image = soup_link.find("meta", property="og:image")['content']
            except (TypeError, ValueError):
                print('ghafla: No image found')

            news_dict = {
                'category': 'entertainment',
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


def get_sde():
    sde_url = 'https://www.sde.co.ke/'
    if check_connection(sde_url):
        sde = requests.get(sde_url)
        soup = BeautifulSoup(sde.text, 'lxml')
        top_story = soup.select('.top-stories-1 a')
        medium_stories = soup.select('.top-stories-2 a', limit=2)
        img_group = soup.select('.latest-story-img-home-3 a', limit=4)
        top_stories = soup.select('.tf-stories > div a', limit=4)
        sde_stories = top_story + medium_stories + img_group + top_stories
        sde = []
        for link in soup.select('a.news__link', limit=10):
            news_title = '{}({})'.format(link.get_text(), link.get('href'))
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
                'category': 'entertainment',
                'source': 'sde',
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
            sde.append(news_dict)
        return sde


def get_mpasho():
    mpasho_url = 'https://mpasho.co.ke/latest/'
    if check_connection(mpasho_url):
        mpasho = requests.get(mpasho_url, headers=headers)
        soup = BeautifulSoup(mpasho.text, 'lxml', parse_only=SoupStrainer('h3'))
        mpasho = []
        for link in soup.select('h3.entry-title a', limit=10):
            mpasho_link = requests.get(link.get('href'))
            soup_link = BeautifulSoup(mpasho_link.text, 'lxml', parse_only=SoupStrainer(['p', 'meta']))

            # Titles have weird '...' at the end, so we get the title in the meta tags
            title = ''
            try:
                title = soup_link.find("meta", property="og:title")['content']
            except (TypeError, ValueError):
                print('Mpasho: No title meta')
                continue
            news_title = '{}({})'.format(title, link.get('href'))

            article_date = ''
            try:
                article_date = soup_link.find("meta", property="article:published_time")['content']
            except (TypeError, ValueError):
                print('Mpasho: No article date meta')
                continue

            # Get image
            image = ''
            try:
                image = soup_link.find("meta", property="og:image")['content']
            except (TypeError, ValueError):
                print('Mpasho: No image found')

            news_dict = {
                'category': 'entertainment',
                'source': 'mpasho',
                'title': title,
                'link': link.get('href'),
                'image': image,
                'content': [link_inner.get_text().strip(' ,.-') for link_inner in
                            soup_link.select('p', limit=2)],
                'date': article_date,
                'date_added': datetime.datetime.utcnow()
            }
            collection.update({'link': link.get('href')}, news_dict, upsert=True)
            mpasho.append(news_dict)
        return mpasho


def get_ent():
    get_tuko()
    get_ghafla()
    get_sde()
    get_mpasho()
