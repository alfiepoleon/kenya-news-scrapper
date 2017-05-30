import json
import requests
from bs4 import BeautifulSoup, SoupStrainer
from datetime import date

'''
This is to run from the python console, returns news in the python console.
'''
today = date.today()


def get_tuko():
    tuko = requests.get('https://www.tuko.co.ke/arts-and-entertainment')
    soup = BeautifulSoup(tuko.text, 'lxml')

    for link in soup.select('a.news__link', limit=10):
        print(link.get_text(), link.get('href'))
        tuko_link = requests.get(link.get('href'))
        soup_link = BeautifulSoup(tuko_link.text, 'lxml')
        for link_inner in soup_link.select('p.align-left > strong', limit=3):
            print('\t', link_inner.get_text().strip())
        print('\n')


def get_ghafla():
    ghafla_url = 'http://www.ghafla.com/ke/entertainment/'
    ghafla = requests.get(ghafla_url)
    print(ghafla)
    soup = BeautifulSoup(ghafla.text, 'lxml', parse_only=SoupStrainer('div'))
    for article in soup.select('div.omega', limit=10):
        article_link = article.a
        link = article_link['href']
        title = article_link.get_text()
        summary = article.p.get_text().strip()
        print(title, link)
        print('\t', summary, '\n')


def get_all_ent():
    get_tuko()
    get_ghafla()
