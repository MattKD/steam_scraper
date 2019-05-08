# steam_scraper
Tiny Python library to scrape app data from the Steam store


The Steam store may change its HTML structure at any time, so these functions could fail at some point. Run `python -m pytest` to check if they still work. Run `pip install .` to install, which will also install lxml, pycurl, and certifi. If on Windows, pycurl and lxml may fail to install, and will need to be installed manually. https://www.lfd.uci.edu/~gohlke/pythonlibs/ has Windows pycurl and lxml binaries, which can be installed with `pip install somelib.whl`. 


## Example
```
import steam_scraper.scraper as scraper

curl = scraper.createCurl()
applist = scraper.getAppList()
for appid in applist:
  try:
    doc = scraper.getAppDoc(appid.id, curl)
    app_data = scraper.scrapeAppDoc(doc)
  except scraper.RequestException: # many appid's are no longer valid and will raise RequestException
    pass
  # use data
  # sleep so you don't download too fast; probably 1-10 req/sec is safe
curl.close()
```

## steam_scraper.scraper.py types
```
class ScrapeException(Exception):
  pass

class RequestException(Exception):
  pass

class AppID():
  id :: str
  name :: str
  
class AppData():
  release_date :: datetime.date
  num_reviews :: int
  num_positive :: int
  meta_score :: int or None
  type :: str # 'game', 'dlc', 'software', 'hardware'
  price :: float
  developer :: str or None
  tags :: {name :: str : count :: int}

```

## steam_scraper.scraper.py function
```
getAppList():
  Returns: [AppID]
  Raises: RequestException
  # Gets list of all apps on Steam store, some of which are dead. Includes games, dlc, software, and hardware.
  
getAppUrl(app_id):
  Params: app_id::int
  Returns: url::str
  # Constructs url from AppID.id for use with getResponseText.
  
createCurl():
  Returns: pycrl.Curl
  # Creates curl object with needed cookie. close method must be called when done.
  
getResponseText(url, curl):
  Params: url::str, curl::pycurl.Curl
  Returns: html::str
  Raises: RequestException
  # Gets the store page html.

textToDoc(html):
  Params: html::str
  Returns: lxml.etree._Element
  # Parses the response html into an lxml document for use with scrape functions.
  
getAppDoc(id, curl):
  Params: id::int, curl::pycurl.Curl
  Returns: lxml.etree._Element
  Raises: RequestException
  # Gets the store html and parses into lxml document.
  
scrapeAppDocNumReviews(doc):
  Params: doc::lxml.etree._Element
  Returns: (num_reviews::int, num_positive::int)
  Raises: ScrapeException
  # Gets the number of reviews and number of positive reviews. User score is num_positive / num_reviews.
  
scrapeAppDocReleaseDate(doc):
  Params: doc::lxml.etree._Element
  Returns: datetime.date or None
  Raises: ScrapeException
  # Gets the release date or None if the date couldn't be parsed, for example with "Coming Soon" dates.
  
scrapeAppDocMetaScore(doc):
  Params: doc::lxml.etree._Element
  Returns: meta_score::int or None 
  # Gets the metascore if there is one, or None.
  
scrapeAppDocTags(doc):
  Params: doc::lxml.etree._Element
  Returns: {name::string : votes::int}
  # Get all the tags and the number of user votes for each tag.
  
scrapeAppDocType(doc):
  Params: doc::lxml.etree._Element
  Returns: type::str
  Raises: ScrapeException
  # Get the app type, which is one of 'game', 'dlc', 'software', or 'hardware'.
  
scrapeAppDocPrice(doc):
  Params: doc::lxml.etree._Element
  Returns: price::float
  Raises: ScrapeException
  # Get the app price, which is 0 is free.
  
scrapeAppDocDeveloper(doc):
  Params: doc::lxml.etree._Element
  Returns: developer::str or None
  # Get developer of game, dlc, or software.

scrapeAppDoc(doc):
  Params: doc::lxml.etree._Element
  Returns: AppData
  # Gets all data from other scraping functions.
  
```
