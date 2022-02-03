import requests
from bs4 import BeautifulSoup

def scrape(WebUrl):
  url = WebUrl
  code = requests.get(url)
  plain = code.text
  soup = BeautifulSoup(plain, "html.parser")

  div = soup.find('div', {'class': 'l-card-11'})
  problem_title = div.find('p', {'class': 'm-card-11_head-2'}).text
  anchor = div.find('a', {'class': 'm-button-1'})
  link = url + anchor.get('href')
  return {
    "problem_title": problem_title,
    "link": link
  }