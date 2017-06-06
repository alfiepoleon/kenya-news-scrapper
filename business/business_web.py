import datetime
import json
import os

import dateutil.parser
import requests
from bs4 import BeautifulSoup, SoupStrainer
from pymongo import MongoClient
from pytz import timezone

from check_connection import check_connection

"""

"""
today = datetime.date.today()
localtz = timezone('Africa/Nairobi')

# Configure the connection to the database
client = MongoClient(os.environ['MongoDB_URI'])
db = client['kenya-news']  # Select the database
collection = db.business


def get_capital():
    capital_url = 'http://www.capitalfm.co.ke/business/{}/{:02}'.format(today.year, today.month)
    if check_connection(capital_url):
        capital = requests.get(capital_url)
        soup = BeautifulSoup(capital.text, 'lxml', parse_only=SoupStrainer('div'))
        capital = []
        for article in soup.select('div.entry-information'):
            article_link = article.a
            link = article_link['href']
            title = article_link.get_text()

            # To strip the date and location ahead of an article summary
            try:
                summary = article.p.get_text().split('-')[1].strip()
            except IndexError:
                summary = article.p.get_text().strip()

            capital_link = requests.get(link)
            soup_link = BeautifulSoup(capital_link.text, 'lxml', parse_only=SoupStrainer(['meta', 'img']))
            article_date = soup_link.find("meta", property="article:published_time")['content']
            image = ''
            try:
                image = soup_link.find("meta", property="og:image")['content']
            except (TypeError, ValueError):
                try:
                    image = soup_link.find('img', class_='size-full')['src']
                except (TypeError, ValueError):
                    print('Capital: No image found')

            news_dict = {
                'category': 'business',
                'source': 'capital',
                'title': title,
                'link': link,
                'image': image,
                'content': [summary],
                'date': article_date,
                'date_added': datetime.datetime.utcnow()
            }
            collection.update({'link': link}, news_dict, upsert=True)
            capital.append(news_dict)
        return capital


def get_standard():
    standard_url = 'https://www.standardmedia.co.ke/business/category/19/business-news'
    if check_connection(standard_url):
        standard = requests.get(standard_url)
        soup = BeautifulSoup(standard.text, 'lxml', parse_only=SoupStrainer('div'))
        standard = []
        for link in soup.select('h4 a', limit=14):
            if link.get_text():
                news_title = '{}({})'.format(link.get_text().strip(), link.get('href'))
                standard_link = requests.get(link.get('href'))
                soup_link = BeautifulSoup(standard_link.text, 'lxml', parse_only=SoupStrainer(['script']))
                article_date = 0
                content = ''
                image = ''
                try:
                    data = json.loads(soup_link.find('script', type='application/ld+json').text.replace("\\", r"\\"))
                    article_date = data['dateModified']
                    content = data['description']
                    image = data['image']['url']
                    if image == 'https://www.standardmedia.co.ke':
                        image = ''
                    print(image)
                except ValueError:
                    print('Standard: invalid json detected')
                    continue

                news_dict = {
                    'category': 'business',
                    'source': 'standard',
                    'title': link.get_text().strip(),
                    'link': link.get('href'),
                    'image': image,
                    'content': content,
                    'date': article_date,
                    'date_added': datetime.datetime.utcnow()
                }
                collection.update({'link': link.get('href')},
                                  news_dict, upsert=True)
                standard.append(news_dict)
        return standard


def get_nation():
    nation_url = 'http://www.nation.co.ke/business'
    if check_connection(nation_url):
        nation = requests.get(nation_url)
        soup = BeautifulSoup(nation.text, 'lxml', parse_only=SoupStrainer(['div', 'section']))
        top_teaser = soup.select('.story-teaser.top-teaser > h1 > a')
        medium_teasers = soup.select('.story-teaser.medium-teaser > h2 > a', limit=10)
        small_story_list = soup.select('.small-story-list a', limit=10)
        nation_stories = top_teaser + medium_teasers + small_story_list
        nation = []
        for link in nation_stories:
            if link.get('href').startswith('http'):
                complete_link = link.get('href')
            else:
                complete_link = 'http://www.nation.co.ke{}'.format(link.get('href'))
            news_title = '{}({})'.format(link.get_text(), complete_link)

            # Nation is slow to parse and often leads to connection errors
            # Just to make sure one article failing doesn't lead to all nation links failing
            try:
                nation_link = requests.get(complete_link)
            except ConnectionError:
                print('Connection error at {}, moving on...'.format(complete_link))
                continue
            soup_link = BeautifulSoup(nation_link.text, 'lxml', parse_only=SoupStrainer(['meta', 'section']))
            article_date = 0
            image = ''
            try:
                article_date = soup_link.find("meta", property="og:article:modified_time")['content']
                # Nation's date isn't in ISO and doesn't have timezone info like the rest, so fixing that...
                parsed_article_date = dateutil.parser.parse("{}".format(article_date))
                # There is a disparity between the published or modified time from the meta tags,
                # and the time it actually goes live, like 3 hours, give or take, fixing that...
                parsed_article_date += datetime.timedelta(hours=3)
                tz_aware = localtz.localize(parsed_article_date)
                article_date = tz_aware.isoformat()

                # Get image from meta tags
                image = soup_link.find("meta", property="og:image")['content']
            except (TypeError, ValueError):
                try:
                    article_date = soup_link.find("meta", property="og:article:published_time")['content']
                    # Nation's date isn't in ISO and doesn't have timezone info like the rest, so fixing that...
                    parsed_article_date = dateutil.parser.parse("{}".format(article_date))
                    # There is a disparity between the published or modified time from the meta tags,
                    # and the time it actually goes live, like 3 hours, give or take, fixing that...
                    parsed_article_date += datetime.timedelta(hours=3)
                    tz_aware = localtz.localize(parsed_article_date) + datetime.timedelta(hours=3)
                    article_date = tz_aware.isoformat()

                    # Get image from meta tags
                    image = soup_link.find("meta", property="og:image")['content']
                except (TypeError, ValueError):
                    print('Nation: Invalid date meta detected')
                    continue
            news_dict = {
                'category': 'business',
                'source': 'nation',
                'title': link.get_text(),
                'link': complete_link,
                'image': image,
                'content': [link_inner.get_text().strip() for link_inner in
                            soup_link.select('section.summary > div > ul li')],
                'date': article_date,
                'date_added': datetime.datetime.utcnow()
            }
            collection.update({'link': complete_link}, news_dict, upsert=True)
            nation.append(news_dict)
        return nation


def get_the_star():
    star_url = 'http://www.the-star.co.ke/sections/business_c29663'
    if check_connection(star_url):
        star = requests.get(star_url)
        soup = BeautifulSoup(star.text, 'lxml')
        top_stories = soup.select('.field.field-name-title > h1 > a', limit=20)
        star_stories = top_stories
        star = []
        for link in star_stories:
            complete_link = 'http://www.the-star.co.ke{}'.format(link.get('href'))
            news_title = '{}({})'.format(link.get_text(), complete_link)
            star_link = requests.get(complete_link)
            soup_link = BeautifulSoup(star_link.text, 'lxml')
            article_date = 0
            image = ''
            try:
                article_date = soup_link.find("meta", property="og:updated_time")['content']

                # Get image from meta tags
                image = soup_link.find("meta", property="og:image")['content']
            except (TypeError, ValueError):
                print('Star: invalid date meta detected')
            news_dict = {
                'category': 'business',
                'source': 'star',
                'title': link.get_text(),
                'link': complete_link,
                'image': image,
                'content': [link_inner.get_text() for link_inner in
                            soup_link.select('.field.field-name-body p', limit=2)],
                'date': article_date,
                'date_added': datetime.datetime.utcnow()
            }
            collection.update({'link': complete_link}, news_dict, upsert=True)
            star.append(news_dict)
        return star


def get_business_daily():
    business_daily_url = 'http://www.businessdailyafrica.com/'
    if check_connection(business_daily_url):
        business_daily = requests.get(business_daily_url)
        soup = BeautifulSoup(business_daily.text, 'lxml')
        featured = soup.select('article.article-list-featured')
        list_grid = soup.select('article.article-list-grid')
        business_daily_stories = featured + list_grid
        business_daily = []
        for _ in business_daily_stories:
            link = _.a

            # Format link
            if link.get('href').startswith('http'):
                complete_link = link.get('href')
            else:
                complete_link = 'http://www.businessdailyafrica.com/{}'.format(link.get('href'))

            business_daily_link = requests.get(complete_link)
            soup_link = BeautifulSoup(business_daily_link.text, 'lxml')

            title = soup_link.title.string.split('-')[0].strip()

            # Some titles are just 'Business Daily'
            if title == 'Business Daily':
                title = soup_link.find("meta", itemprop="name")['content'].strip()
            # Get image from meta tags
            image = ''
            try:
                image = soup_link.find("meta", property="og:image")['content']
            except (TypeError, ValueError):
                print('business_daily: invalid image meta detected')

            article_date = 0
            try:
                article_date = soup_link.find("meta", property="og:updated_time")['content']

            except (TypeError, ValueError):
                print('business_daily: invalid date meta detected')
            news_dict = {
                'category': 'business',
                'source': 'business_daily',
                'title': title,
                'link': complete_link,
                'image': image,
                'content': [link_inner.get_text() for link_inner in soup_link.select('.page-box-inner p', limit=2)],
                'date': article_date,
                'date_added': datetime.datetime.utcnow()
            }
            collection.update({'link': complete_link}, news_dict, upsert=True)
            business_daily.append(news_dict)
        return business_daily


def get_kenyan_wall_street():
    url = 'http://kenyanwallstreet.com/category/kenyan-news'
    if check_connection(url):
        ghafla = requests.get(url)
        soup = BeautifulSoup(ghafla.text, 'lxml', parse_only=SoupStrainer('div'))
        news_arr = []
        for article in soup.select('div.mh-posts-list-content', limit=10):
            article_link = article.a
            link = article_link['href']
            title = article_link.get_text().strip()
            summary = article.find('div', class_='mh-excerpt').get_text().strip()
            print(summary)
            kenyan_wall_street_link = requests.get(link)
            soup_link = BeautifulSoup(kenyan_wall_street_link.text, 'lxml', parse_only=SoupStrainer('meta'))
            print(title, link)
            article_date = soup_link.find("meta", property="article:published_time")['content']
            image = ''
            try:
                image = soup_link.find("meta", property="og:image")['content']
            except (TypeError, ValueError):
                print('Kenyan Wall Street: No image found')

            news_dict = {
                'category': 'business',
                'source': 'kenyan_wall_street',
                'title': title,
                'link': link,
                'image': image,
                'content': [summary],
                'date': article_date,
                'date_added': datetime.datetime.utcnow()
            }
            collection.update({'link': link}, news_dict, upsert=True)
            news_arr.append(news_dict)
        return ghafla


def get_business():
    get_capital()
    get_standard()
    get_the_star()
    get_nation()
    get_business_daily()
    get_kenyan_wall_street()
