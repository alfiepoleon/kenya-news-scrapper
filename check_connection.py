import requests
from requests.exceptions import ConnectionError, Timeout, HTTPError, TooManyRedirects
import sys


def check_connection(url):
    try:
        request = requests.head(url)
        if request.status_code == 200:
            print('Connection ok...')
            return True
        elif request.status_code == 301:
            print('Connection redirect')
            return True
        else:
            print('Error connecting')
            return False
    except (ConnectionError, Timeout):
        print('{} can not be reached, check your connection and retry later'.format(url))
        return False

    except (HTTPError, TooManyRedirects):
        print('There is an issue with the url, {}, confirm it, or retry later'.format(url))
        return False

