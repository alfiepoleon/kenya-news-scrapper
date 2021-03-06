import json
import requests
from bs4 import BeautifulSoup, SoupStrainer
from pymongo import MongoClient
import datetime
import dateutil.parser
from pytz import timezone
import os
from check_connection import check_connection
from get_content import get_content

"""
This is used by flask, returns json, example:
{
    "_id" : ObjectId("5927ed7e699a164e8d6de4bd"),
    "category": "news",
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
client = MongoClient(os.environ['MongoDB_URI'])
db = client['kenya-news']  # Select the database
collection = db.news


def get_tuko():
    tuko_url = 'https://www.tuko.co.ke'
    if check_connection(tuko_url):
        tuko = requests.get(tuko_url)
        soup = BeautifulSoup(tuko.text, 'lxml', parse_only=SoupStrainer('a'))
        tuko = []
        for link in soup.select('a.news__link', limit=6):
            news_title = '{}({})'.format(link.get_text(), link.get('href'))
            tuko_link = requests.get(link.get('href'))
            soup_link = BeautifulSoup(tuko_link.text, 'lxml', parse_only=SoupStrainer(['p', 'meta', 'img']))
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
                'category': 'news',
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


def get_capital():
    capital_url = 'http://www.capitalfm.co.ke/news/{}/{:02}'.format(today.year, today.month)
    if check_connection(capital_url):
        capital = requests.get(capital_url)
        soup = BeautifulSoup(capital.text, 'lxml', parse_only=SoupStrainer('div'))
        capital = []
        for article in soup.select('div.entry-information'):
            article_link = article.a
            link = article_link['href']
            title = article_link.get_text()
            capital_link = requests.get(link)
            soup_link = BeautifulSoup(capital_link.text, 'lxml', parse_only=SoupStrainer(['meta', 'img', 'div']))
            article_date = soup_link.find("meta", property="article:published_time")['content']
            image = ''
            try:
                image = soup_link.find("meta", property="og:image")['content']
            except (TypeError, ValueError):
                try:
                    image = soup_link.find('img', class_='size-full')['src']
                except (TypeError, ValueError):
                    print('Capital: No image found')

            try:
                content = get_content(soup_link, 'entry-content').split('\u2013')[1].strip()
            except IndexError:
                content = get_content(soup_link, 'entry-content').strip()
            news_dict = {
                'category': 'news',
                'source': 'capital',
                'title': title,
                'link': link,
                'image': image,
                'content': content,
                'date': article_date,
                'date_added': datetime.datetime.utcnow()
            }
            collection.update({'link': link}, news_dict, upsert=True)
            capital.append(news_dict)
        return capital


def get_standard():
    standard_url = 'https://www.standardmedia.co.ke/'
    if check_connection(standard_url):
        standard = requests.get(standard_url)
        soup = BeautifulSoup(standard.text, 'lxml', parse_only=SoupStrainer('div'))
        standard = []
        for link in soup.select('.col-xs-8.zero a', limit=11):
            if link.get_text():
                news_title = '{}({})'.format(link.get_text().strip(), link.get('href'))
                standard_link = requests.get(link.get('href'))
                soup_link = BeautifulSoup(standard_link.text, 'lxml', parse_only=SoupStrainer(['script', 'div']))
                try:
                    data = json.loads(soup_link.find('script', type='application/ld+json').text.replace("\\", r"\\"))
                    article_date = data['dateModified']
                    image = data['image']['url']
                    if image == 'https://www.standardmedia.co.ke':
                        image = ''
                except (ValueError, AttributeError):
                    print('Standard: invalid json detected')
                    continue
                try:
                    content = get_content(soup_link, 'main-article')
                except AttributeError:
                    try:
                        content = get_content(soup_link, 'story')
                    except AttributeError:
                        print('Standard: No content found')
                        continue

                news_dict = {
                    'category': 'news',
                    'source': 'standard',
                    'title': link.get_text().strip(),
                    'link': link.get('href'),
                    'image': image,
                    'content': content,
                    'date': article_date,
                    'date_added': datetime.datetime.utcnow()
                }
                collection.update({'link': link.get('href')}, news_dict, upsert=True)
                standard.append(news_dict)
        return standard


def get_nation():
    nation_url = 'http://www.nation.co.ke/'
    if check_connection(nation_url):
        nation = requests.get(nation_url)
        soup = BeautifulSoup(nation.text, 'lxml', parse_only=SoupStrainer(['div', 'section']))
        top_teaser = soup.select('.story-teaser.top-teaser > h1 > a')
        medium_teasers = soup.select('.story-teaser.medium-teaser > h2 > a', limit=3)
        small_teasers = soup.select('.story-teaser.small-teaser > h2 > a', limit=3)
        gallery_words = soup.select('.gallery-words a', limit=6)
        small_story_list = soup.select('.small-story-list a', limit=7)
        nation_stories = top_teaser + medium_teasers + small_teasers + gallery_words + small_story_list
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
                print('Nation news: connection error at {}, moving on...'.format(complete_link))
                continue
            soup_link = BeautifulSoup(nation_link.text, 'lxml', parse_only=SoupStrainer(['meta', 'section']))
            try:
                article_date = soup_link.find("meta", property="og:article:published_time")['content']
                # Nation's date isn't in ISO and doesn't have timezone info like the rest, so fixing that...
                parsed_article_date = dateutil.parser.parse("{}".format(article_date))
                # There is a disparity between the published or modified time from the meta tags,
                # and the time it actually goes live, like 3 hours, give or take, fixing that...
                # parsed_article_date += datetime.timedelta(hours=3)
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
                    tz_aware = localtz.localize(parsed_article_date)
                    article_date = tz_aware.isoformat()

                    # Get image from meta tags
                    image = soup_link.find("meta", property="og:image")['content']
                except (TypeError, ValueError):
                    print('Nation: Invalid date meta detected')
                    continue
            try:
                content = get_content(soup_link, 'body-copy')
            except AttributeError:
                try:
                    content = get_content(soup_link, 'caption-container')
                except AttributeError:
                    print('Nation: No content found')
                    continue
            news_dict = {
                'category': 'news',
                'source': 'nation',
                'title': link.get_text(),
                'link': complete_link,
                'image': image,
                'content': content,
                'date': article_date,
                'date_added': datetime.datetime.utcnow()
            }
            collection.update({'link': complete_link}, news_dict, upsert=True)
            nation.append(news_dict)
        return nation


def get_the_star():
    star_url = 'http://www.the-star.co.ke/'
    if check_connection(star_url):
        star = requests.get(star_url)
        soup = BeautifulSoup(star.text, 'lxml')
        top_stories = soup.select('.field.field-name-title > h1 > a', limit=7)
        medium_stories = soup.select('h1.field-content > a', limit=10)
        star_stories = top_stories + medium_stories
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
            content = get_content(soup_link, 'field-name-body')
            news_dict = {
                'category': 'news',
                'source': 'star',
                'title': link.get_text(),
                'link': complete_link,
                'image': image,
                'content': content,
                'date': article_date,
                'date_added': datetime.datetime.utcnow()
            }
            collection.update({'link': complete_link}, news_dict, upsert=True)
            star.append(news_dict)
        return star


def get_news():
    get_tuko()
    get_capital()
    get_standard()
    get_the_star()
    get_nation()
