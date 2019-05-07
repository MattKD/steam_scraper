import pytest
import steam_scraper.scraper as scraper
import lxml.etree
import datetime
import os 
from time import sleep

curl = None
counter_strike_html = None

def finish_tests():
  curl.close()

@pytest.fixture(scope="session", autouse=True)
def start_tests(request):
  global curl
  global counter_strike_html
  dir_path = os.path.dirname(os.path.realpath(__file__))
  test_path = os.path.join(dir_path, 'counter-strike.html')

  with open(test_path, 'r', errors='backslashreplace') as f:
    counter_strike_html = f.read()

  curl = scraper.createCurl()
  request.addfinalizer(finish_tests)

def test_getAppList():
  applist = scraper.getAppList()
  assert applist is not None
  assert len(applist) > 50000
  app = applist[0]
  assert type(app) is scraper.AppID

def test_getAppUrl():
  id = 10
  expected_url = "https://store.steampowered.com/app/" + str(id)
  assert scraper.getAppUrl(id) == expected_url

def test_getResponseText():
  url = scraper.getAppUrl(10)
  html = scraper.getResponseText(url, curl)

  url = scraper.getAppUrl(-1)
  try:
    html = scraper.getResponseText(url, curl)
  except scraper.RequestException:
    pass

def test_textToDoc():
  doc = scraper.textToDoc(counter_strike_html)
  assert type(doc) is lxml.etree._Element

def test_getAppDoc():
  id = 10
  doc = scraper.getAppDoc(id, curl)
  assert type(doc) is lxml.etree._Element

def test_scrapeAppDocNumReviews():
  doc = scraper.textToDoc(counter_strike_html)
  num_revs, num_pos = scraper.scrapeAppDocNumReviews(doc)
  assert num_revs > 50000 and num_pos > 50000

def test_scrapeAppDocReleaseDate():
  doc = scraper.textToDoc(counter_strike_html)
  date = scraper.scrapeAppDocReleaseDate(doc)
  assert type(date) is datetime.date
  assert date == datetime.date(2000, 11, 1)

def test_scrapeAppDocMetaScore():
  doc = scraper.textToDoc(counter_strike_html)
  score = scraper.scrapeAppDocMetaScore(doc)
  assert type(score) is int
  assert score == 88

def test_scrapeAppDocTags():
  doc = scraper.textToDoc(counter_strike_html)
  tags = scraper.scrapeAppDocTags(doc)
  assert len(tags) > 0
  assert 'Action' in tags
  assert 'FPS' in tags
  for k, v in tags.items():
    assert type(k) is str
    assert type(v) is int
    assert v > 0

def test_scrapeAppDocType():
  doc = scraper.textToDoc(counter_strike_html)
  type = scraper.scrapeAppDocType(doc)
  assert type == 'game'

def test_scrapeAppDocPrice():
  doc = scraper.textToDoc(counter_strike_html)
  price = scraper.scrapeAppDocPrice(doc)
  assert price > 0

def test_scrapeAppDocDeveloper():
  doc = scraper.textToDoc(counter_strike_html)
  developer = scraper.scrapeAppDocDeveloper(doc)
  assert developer == 'Valve'

def test_scrapeAppDoc():
  doc = scraper.textToDoc(counter_strike_html)
  app_data = scraper.scrapeAppDoc(doc)
  assert type(app_data) is scraper.AppData
  assert app_data.release_date == datetime.date(2000, 11, 1)
  assert len(app_data.tags) > 0
  assert app_data.meta_score == 88
  assert app_data.num_reviews > 50000
  assert app_data.num_positive > 50000
  assert app_data.type == 'game'
  assert app_data.price > 0
  assert app_data.developer == 'Valve'

def test_scrape_counter_strike():
  sleep(.25)
  doc = scraper.getAppDoc(10, curl)
  assert type(doc) is lxml.etree._Element
  app_data = scraper.scrapeAppDoc(doc)
  assert app_data.release_date == datetime.date(2000, 11, 1)
  assert app_data.num_reviews > 0
  assert app_data.num_positive > 0
  assert app_data.meta_score > 0
  assert 'Action' in app_data.tags
  assert app_data.type == 'game'
  assert app_data.developer == 'Valve'

def test_scrape_doom():
  sleep(.25)
  doc = scraper.getAppDoc(379720, curl)
  assert type(doc) is lxml.etree._Element
  app_data = scraper.scrapeAppDoc(doc)
  assert app_data.release_date == datetime.date(2016, 5, 12)
  assert app_data.num_reviews > 0
  assert app_data.num_positive > 0
  assert app_data.meta_score > 0
  assert 'Action' in app_data.tags
  assert app_data.type == 'game'
  assert app_data.price > 0
  assert app_data.developer == 'id Software'

def test_scrape_hollow_knight_ost():
  sleep(.25)
  doc = scraper.getAppDoc(598190, curl)
  assert type(doc) is lxml.etree._Element
  app_data = scraper.scrapeAppDoc(doc)
  assert app_data.release_date == datetime.date(2017, 2, 24)
  assert app_data.num_reviews > 0
  assert app_data.num_positive > 0
  assert 'Soundtrack' in app_data.tags
  assert app_data.type == 'dlc'
  assert app_data.price > 0
  assert app_data.developer == 'Team Cherry'

def test_scrape_blender():
  sleep(.25)
  doc = scraper.getAppDoc(365670, curl)
  assert type(doc) is lxml.etree._Element
  app_data = scraper.scrapeAppDoc(doc)
  assert app_data.release_date == datetime.date(2015, 7, 3)
  assert app_data.num_reviews > 0
  assert app_data.num_positive > 0
  assert 'Animation & Modeling' in app_data.tags
  assert app_data.type == 'software'
  assert app_data.developer == 'Blender Foundation'

def test_scrape_steam_controller():
  sleep(.25)
  doc = scraper.getAppDoc(353370, curl)
  assert type(doc) is lxml.etree._Element
  app_data = scraper.scrapeAppDoc(doc)
  assert app_data.release_date == datetime.date(2015, 11, 10)
  assert app_data.num_reviews > 0
  assert app_data.num_positive > 0
  assert 'Controller' in app_data.tags
  assert app_data.type == 'hardware'
  assert app_data.price > 0
  assert app_data.developer is None



