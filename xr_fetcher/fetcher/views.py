import logging
import datetime
import pytz

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
    def get(self, request, format=None):
        resp = {
            'rates': {
                'dof': None,
                'fixer': None,
                'banxico': None
            }
        }

        # DOF data retrieval
        data = None
        try:
            html = scraper.fetchHTML()
            data = scraper.scrapeHTML(html)
        except Exception as e:
            log.error("Fetch Rates Exception: {}", e)
            data = None

        if data != None:
            # We assume all data from DOF is updated at 12:00, as described in footnote 2 in the exchange rate site
            # https://www.banxico.org.mx/tipcamb/tipCamMIAction.do
            tzdate = data['date'] + 'T12:00:00'
            date = datetime.datetime.strptime(tzdate, '%d/%m/%YT%H:%M:%S')

            tz = pytz.timezone('America/Mexico_City')
            tz_date = tz.localize(date)

            # We are using ISO 8601 for all response dates
            resp['rates']['dof'] = {
                "last_updated": tz_date.isoformat(),
                "value": data['value']
            }

        # Fixer data retrieval
        # Banxico data retrieval
        return Response(resp)
