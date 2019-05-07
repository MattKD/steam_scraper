import json
import re
import datetime
import pycurl
import certifi
from io import BytesIO
from lxml import etree

class ScrapeException(Exception):
  pass

class RequestException(Exception):
  pass

class AppID():
  def __init__(self, id, name):
    self.id = id
    self.name = name

  def __eq__(self, o):
    return self.id == o.id and self.name == o.name

  def __lt__(self, o):
    return self.id < o.id

  def __repr__(self):
    return 'AppID({}, {})'.format(self.id, repr(self.name))

class AppData():
  def __init__(self, release_date, num_reviews, num_positive,
               meta_score, app_type, price, developer, tags):
    self.release_date = release_date
    self.num_reviews = num_reviews
    self.num_positive = num_positive
    self.meta_score = meta_score
    self.type = app_type
    self.price = price
    self.developer = developer
    self.tags = tags

  def __eq__(self, o):
    return self.release_date == o.release_date and \
        self.num_reviews == o.num_reviews and \
        self.num_positive == o.num_positive and \
        self.meta_score == o.meta_score and \
        self.type == o.type and \
        self.price == o.price and \
        self.developer == o.developer and \
        self.tags == o.tags

  def __repr__(self):
    return ('AppData(developer={}, release_date={}, ' + \
        'type={}, num_reviews={}, num_positive={}, ' + \
        'meta_score={}, price={}, tags={})').\
        format(self.developer, repr(self.release_date), 
               self.type, self.num_reviews, self.num_positive,
               self.meta_score, self.price, repr(self.tags))

def getAppList():
  '''
  Returns: [AppID]
  Raises: RequestException
  '''
  url = "http://api.steampowered.com/ISteamApps/GetAppList/v2"
  curl = createCurl()
  try:
    res = getResponseText(url, curl)
  finally:
    curl.close()
  apps = json.loads(res)['applist']['apps']
  return [AppID(app['appid'], app['name']) for app in apps]

  return None

def getAppUrl(app_id):
  '''
  Params: app_id::int
  Returns: url::str
  '''
  return "https://store.steampowered.com/app/" + str(app_id)

def createCurl():
  '''
  Returns pycrl.Curl
  '''
  cookies = "Cookie: lastagecheckage=1-January-2000; birthtime=946702801"
  c = pycurl.Curl()
  c.setopt(c.CAINFO, certifi.where())
  c.setopt(c.HTTPHEADER, [cookies])
  c.setopt(c.TIMEOUT, 10)
  return c

def getResponseText(url, curl):
  '''
  Params: url::str, curl::pycurl.Curl
  Returns: html::str
  Raises: RequestException
  '''
  buffer = BytesIO()
  try:
    curl.setopt(curl.URL, url)
    curl.setopt(curl.WRITEDATA, buffer)
    curl.perform()
    status_code = curl.getinfo(curl.RESPONSE_CODE)
  except pycurl.error as e:
    raise RequestException(str(e))

  if status_code != 200:
    raise RequestException("Error status_code = {}".format(status_code))

  html = buffer.getvalue().decode()
  return html

def textToDoc(text):
  '''
  Params: html::str
  Returns: lxml.etree._Element
  '''
  return etree.HTML(text)

def getAppDoc(id, curl):
  '''
  Params: id::int, curl::pycurl.Curl
  Returns: lxml.etree._Element
  Raises: RequestException
  '''
  url = getAppUrl(id)
  html = getResponseText(url, curl)
  return textToDoc(html)

def scrapeAppDocNumReviews(doc):
  '''
  Params: doc::lxml.etree._Element
  Returns: (num_reviews::int, num_positive::int)
  Raises: ScrapeException
  '''
  num_reviews = 0
  num_positive = 0

  path = './/div[@id="app_reviews_hash"]'
  reviews_el = doc.find(path)
  if reviews_el == None:
    raise ScrapeException

  path = 'input[@id="review_summary_num_reviews"]'
  num_reviews_el = reviews_el.find(path)
  if num_reviews_el != None:
    num_reviews = int(num_reviews_el.get('value').strip())
  path = 'input[@id="review_summary_num_positive_reviews"]'
  num_pos_el = reviews_el.find(path)
  if num_pos_el != None:
    num_positive = int(num_pos_el.get('value').strip())

  return (num_reviews, num_positive)

def scrapeAppDocReleaseDate(doc):
  '''
  Params: doc::lxml.etree._Element
  Returns: datetime.date or None
  Raises: ScrapeException
  '''
  release_date = None

  date_el = doc.find('.//div[@class="release_date"]/div[@class="date"]')
  if date_el == None:
    raise ScrapeException

  date_str = date_el.text
  if date_str == None:
    raise ScrapeException

  date_str = date_str.strip()

  date_fmts = ["%b %d, %Y", "%B %d, %Y", "%b %d %Y", "%B %d %Y", 
               "%b %Y", "%B %Y", "%b, %Y", "%B, %Y", 
               "%Y"]
  for i in range(len(date_fmts)):
    fmt = date_fmts[i]
    try:
      date = datetime.datetime.strptime(date_str, fmt).date()
      release_date = date
      break
    except ValueError:
      if i == len(date_fmts) - 1:
        return None
  
  return release_date

def scrapeAppDocMetaScore(doc):
  '''
  Params: doc::lxml.etree._Element
  Returns: meta_score::int or None 
  '''
  meta_score = None

  divs = doc.findall('.//div[@id="game_area_metascore"]/div')
  for div in divs:
    cls = div.get('class')
    if cls:
      if re.search('score', cls):
        score_str = div.text.strip()
        try:
          meta_score = int(score_str)
        except Exception:
          pass

  return meta_score

def scrapeAppDocTags(doc):
  '''
  Params: doc::lxml.etree._Element
  Returns: {name::string : votes::int}
  '''
  tags = {}

  scripts = doc.findall(".//script")
  tag_details = []
  for script in scripts:
    text = script.text
    if not text:
      continue
    match = re.search(r'InitAppTagModal[^[]+(\[[^\]]+\])', script.text)
    if match:
      tag_details = json.loads(match.group(1))
      for tag in tag_details:
        name = tag['name']
        votes = tag['count']
        if name in tags:
          tags[name] += votes
        else:
          tags[name] = votes
      break

  return tags

def scrapeAppDocType(doc):
  '''
  Params: doc::lxml.etree._Element
  Returns: type::str -- 'game', 'dlc', 'software', 'hardware'
  Raises: ScrapeException
  '''
  links = doc.findall('.//div[@class="breadcrumbs"]/div[@class="blockbg"]/a')
  if links is None:
    raise ScrapeException
  if links[0].text == 'All Games':
    type = 'game'
    for link in links[1:]:
      if link.text == 'Downloadable Content':
        type = 'dlc'
        break
  elif links[0].text == 'All Software':
    type = 'software'
  elif links[0].text == 'All Hardware':
    type = 'hardware'
  else:
    raise ScrapeException
  return type

def scrapeAppDocPrice(doc):
  '''
  Params: doc::lxml.etree._Element
  Returns: price::float
  Raises: ScrapeException
  '''
  meta = doc.find('.//meta[@itemprop="price"]')
  if meta is None:
    raise ScrapeException
  price = float(meta.attrib['content'])
  return price

def scrapeAppDocDeveloper(doc):
  '''
  Params: doc::lxml.etree._Element
  Returns: developer::str or None
  '''
  divs = doc.findall('.//div[@class="details_block"]/div[@class="dev_row"]')
  if divs is None:
    return None

  developer = None
  for div in divs:
    b = div.find('./b')
    if b is None:
      continue
    if b.text == 'Developer:':
      developer = div.find('./a').text
      break

  return developer

def scrapeAppDoc(doc):
  '''
  Params: doc::lxml.etree._Element
  Returns: AppData
  '''
  date = scrapeAppDocReleaseDate(doc)
  (reviews, positive) = scrapeAppDocNumReviews(doc)
  score = scrapeAppDocMetaScore(doc)
  app_type = scrapeAppDocType(doc)
  price = scrapeAppDocPrice(doc)
  dev = scrapeAppDocDeveloper(doc)
  tags = scrapeAppDocTags(doc)
  app_data = AppData(release_date=date, num_reviews=reviews, 
      num_positive=positive, meta_score=score, app_type=app_type, 
      developer=dev, price=price, tags=tags)
  return app_data

