# Kenya News Scrapper

It gets news from [Tuko](https://www.tuko.co.ke), [Capital FM](http://www.capitalfm.co.ke/), [The Standard](https://www.standardmedia.co.ke/), [Daily Nation](http://www.nation.co.ke/news) and [The Star](http://www.the-star.co.ke/), then returns top news from each and a short summary of each article.

There is a cli version and a flask web api version.
### Screenshots
![alt text](https://cloud.githubusercontent.com/assets/14350051/26034663/b061c69c-38c8-11e7-9c6c-cbd23fecc9c3.png)
![alt text](https://cloud.githubusercontent.com/assets/14350051/26034664/b06ca67a-38c8-11e7-87b6-efb5919989bb.png)
![alt text](https://cloud.githubusercontent.com/assets/14350051/26034665/b06d645c-38c8-11e7-817b-90769fceb77e.png)


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

4. Activate the Virtual env

```
source /path/to/new/virtual/environment/bin/activate
```

5. cd to the cloned directory.(The one with requirements.txt) 

6. Install the requirements from requirements.txt

```
pip install -r requirements.txt
```

#### There are two ways to run this script
Run the cli version

```
python scheduler_script.py get_news_cli
```

#### OR

First scrape the news sources to create and fill up the database before running the flask version

```
python scheduler_script.py scrape_news
```
then...

Run app.py to start web server (you can check end points at app.py)

```
python app.py
```

__Note: you can run `python scheduler_script.py delete_old_news` to delete news more that 48 hours old__
## Built With

* [Python HTTP Requests](https://github.com/kennethreitz/requests/) - HTTP for Humans
* [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/) - html parser
* Me ¯\\\_(ツ)_/¯

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details
