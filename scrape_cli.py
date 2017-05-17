import requests
from bs4 import BeautifulSoup
from datetime import date

'''
This is to run from the python console, returns news in the python console.
'''
today = date.today()


def get_tuko():
    tuko = requests.get('https://www.tuko.co.ke')
    soup = BeautifulSoup(tuko.text, 'html.parser')

    for link in soup.select('a.news__link', limit=6):
        print(link.get_text(), link.get('href'))
        tuko_link = requests.get(link.get('href'))
        soup_link = BeautifulSoup(tuko_link.text, 'html.parser')
        for link_inner in soup_link.select('p.align-left > strong', limit=3):
            print('\t', link_inner.get_text())
        print('\n')


def get_capital():
    capital_url = 'http://www.capitalfm.co.ke/news/{}/{:02}'.format(today.year, today.month)
    capital = requests.get(capital_url)
    soup = BeautifulSoup(capital.text, 'html.parser')
    for article in soup.select('div.entry-information'):
        article_link = article.a
        title = article_link['href']
        link = article_link.get_text()
        summary = article.p.get_text().split('-')[1].strip()
        print(title, link)
        print(summary, '\n')


def get_standard():
    standard = requests.get('https://www.standardmedia.co.ke/')
    soup = BeautifulSoup(standard.text, 'html.parser')

    for link in soup.select('.col-xs-8.zero a', limit=11):
        if link.get_text():
            print(link.get_text(), link.get('href'))
            # standard_link = requests.get(link.get('href'))
            # soup_link = BeautifulSoup(standard_link.text, 'html.parser')


def get_nation():
    nation = requests.get('http://www.nation.co.ke/news')
    soup = BeautifulSoup(nation.text, 'html.parser')
    top_teaser = soup.select('.story-teaser.top-teaser > h1 > a')
    medium_teasers = soup.select('.story-teaser.medium-teaser > h2 > a', limit=4)
    tiny_teasers = soup.select('.story-teaser.tiny-teaser > a:nth-of-type(2)')
    nation_stories = top_teaser + medium_teasers + tiny_teasers
    for link in nation_stories:
        complete_link = 'http://www.nation.co.ke{}'.format(link.get('href'))
        print(link.get_text(), complete_link)
        nation_link = requests.get(complete_link)
        soup_link = BeautifulSoup(nation_link.text, 'html.parser')
        # summary_ul = soup_link.select('section.summary > div > ul')
        for link_inner in soup_link.select('section.summary > div > ul li'):
            # print(link_inner)
            print('\t', link_inner.get_text())
        print('\n')


def get_the_star():
    star = requests.get('http://www.the-star.co.ke/')
    soup = BeautifulSoup(star.text, 'html.parser')
    top_stories = soup.select('.field.field-name-title > h1 > a', limit=7)
    medium_stories = soup.select('h1.field-content > a', limit=10)
    star_stories = top_stories + medium_stories
    for link in star_stories:
        complete_link = 'http://www.the-star.co.ke{}'.format(link.get('href'))
        print(link.get_text(), complete_link)
        star_link = requests.get(complete_link)
        soup_link = BeautifulSoup(star_link.text, 'html.parser')
        # summary_ul = soup_link.select('section.summary > div > ul')
        for link_inner in soup_link.select('.field.field-name-body p', limit=2):
            # print(link_inner)
            print('\t', link_inner.get_text())
        print('\n')


def get_all_news():
    # get_tuko()
    get_capital()
    # get_standard()
    # get_nation()
    # get_the_star()


get_all_news()
