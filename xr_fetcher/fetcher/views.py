import logging
import datetime
import pytz
import requests

from django.conf import settings

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

#from . import serializers
from . import scraper

log = logging.getLogger(__name__)

class HelloWorld(APIView):
    permission_classes = [ TokenHasReadWriteScope ]
    def get(self, request, format=None):
        log.info("Hello")
        return Response({"message": "Hello, world!"})

class FetchRates(APIView):
    permission_classes = [ TokenHasReadWriteScope ]

    def fetch_dof_data(self):
        # DOF data retrieval
        s_data = None
        try:
            html = scraper.fetchHTML()
            s_data = scraper.scrapeHTML(html)
        except Exception as e:
            log.error("Fetch Rates Exception: {}", e)
            s_data = None

        if s_data == None:
            return {
                "error": "Could not retrieve data"
            }

        # We assume all data from DOF is updated at 12:00, as described in footnote 2 in the exchange rate site
        # https://www.banxico.org.mx/tipcamb/tipCamMIAction.do
        tzdate = s_data['date'] + 'T12:00:00'
        date = datetime.datetime.strptime(tzdate, '%d/%m/%YT%H:%M:%S')

        tz = pytz.timezone('America/Mexico_City')
        tz_date = tz.localize(date)

        o_data = {
            "last_updated": tz_date.isoformat(),
            "value": s_data['value']
        }
        return o_data

    def fetch_fixer_data(self):
        access_key = settings.FIXER_API_ACCESS_KEY
        base = "MXN"
        symbol = "USD"
        queryString = '?access_key={}&base={}&symbols={}'.format(access_key, base, symbol)
        resp = requests.get(settings.FIXER_BASE_URL + 'latest' + queryString)
        data = resp.json()

        if data['success'] != True:
            return {
                "error": data['error']
            }

        date = datetime.datetime.fromtimestamp(data['timestamp'])

        tz = pytz.timezone('UTC')
        tz_date = tz.localize(date)

        o_data = {
            "last_updated": tz_date.isoformat(),
            "value": data['rates']['USD']
        }
        return o_data

    def get(self, request, format=None):
        resp = {
            'rates': {
                'dof': self.fetch_dof_data(),
                'fixer': self.fetch_fixer_data(),
                'banxico': None
            }
        }

        # Fixer data retrieval
        # Banxico data retrieval
        return Response(resp)
