import logging
import requests

from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

def scrapeHTML(html):
    soup = BeautifulSoup(html, features="html.parser")

    target = soup.find('tr', {"class": "renglonNon"})
    tds = target.find_all('td')

    data = {}
    try:
        data = {
            "date": tds[0].text.strip(),
            "value": float(tds[3].text)
        }
    except Exception as e:
        log.error("Scraper Exception: {}", e)
        data = {
            "error": "scrape failed"
        }
    return data

def fetchHTML():
    page = requests.get('https://www.banxico.org.mx/tipcamb/tipCamMIAction.do')
    return page.content
