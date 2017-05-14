# Kenya News Scrapper

It scrapes news from [Tuko](https:www.tuko.co.ke), [Capital FM](http://www.capitalfm.co.ke/), [The Standard](https://www.standardmedia.co.ke/), [Daily Nation](http://www.nation.co.ke/news) and [The Star](http://www.the-star.co.ke/), then returns top news from each and a summary of each news give you a summary of each article,(except The Standard, I'm yet to figure out a way)

### Prerequisites

```
Python 3 (3.6.1 used in the project)
```

### Installing
pip install requests beautifulsoup4
A step by step series of examples that tell you have to get a development env running in unix systems

1. Clone the repo


2. Setting up a virtual environment, [Python 3 virtual env docs](https://docs.python.org/3/library/venv.html)

```
python3 -m venv /path/to/new/virtual/environment
```

3. Activate the Virtual env

```
cd /path/to/new/virtual/environment
source bin/activate
```
4. cd to the cloned directory.(The one with scape.py)

5. Run __scrape.py__

```
python scrape.py
```


## Built With

* [Python HTTP Requests](https://github.com/kennethreitz/requests/) - HTTP for Humans
* [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/) - html parser
* Me ¯\\\_(ツ)_/¯

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details

