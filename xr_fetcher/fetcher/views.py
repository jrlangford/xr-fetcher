import logging
import datetime
import pytz
import requests
from xml.etree import ElementTree

from django.conf import settings

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from drf_spectacular.utils import extend_schema, inline_serializer

from . import scraper, models, serializers

log = logging.getLogger(__name__)

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
            dv = models.Rate(
                last_updated=None,
                value=None,
                status=models.Success(False, "Could not retrieve data, inspect logs for more information.")
            )
            return dv

        # We assume all data from DOF is updated at 12:00, as described in footnote 2 in the exchange rate site
        # https://www.banxico.org.mx/tipcamb/tipCamMIAction.do
        tzdate = s_data['date'] + 'T12:00:00'
        date = datetime.datetime.strptime(tzdate, '%d/%m/%YT%H:%M:%S')

        tz = pytz.timezone('America/Mexico_City')
        tz_date = tz.localize(date)

        dv = models.Rate(
            tz_date.isoformat(),
            s_data['value'],
            status=models.Success()
        )
        #sv = serializers.RateSerializer(dv).data
        return dv

    def fetch_fixer_data(self):
        access_key = settings.FIXER_API_ACCESS_KEY
        base = "MXN"
        symbol = "USD"
        query_string = '?access_key={}&base={}&symbols={}'.format(access_key, base, symbol)
        resp = requests.get(settings.FIXER_BASE_URL + 'latest' + query_string)
        data = resp.json()

        if data['success'] != True:
            dv = models.Rate(
                last_updated=None,
                value=None,
                status=models.Success(False, "Could not retrieve data: {}".format( data['error']))
            )
            return dv

        date = datetime.datetime.fromtimestamp(data['timestamp'])

        tz = pytz.timezone('UTC')
        tz_date = tz.localize(date)

        dv = models.Rate(
            tz_date.isoformat(),
            data['rates']['USD'],
            status=models.Success()
        )
        #sv = serializers.RateSerializer(dv).data
        return dv

    def fetch_banxico_data(self):
        token = settings.BANXICO_TOKEN
        series_id = 'SF43718'
        query_string = '?mediaType=xml'

        uri = 'series/{}/datos/oportuno'.format(series_id)

        full_url = settings.BANXICO_BASE_URL + uri + query_string

        resp = requests.get(full_url, headers={'Bmx-Token':token})

        if token == '':
            dv = models.Rate(
                last_updated=None,
                value=None,
                status=models.Success(False, "Could not retrieve data: 'Token is empty'")
            )
            return dv

        try:
            root = ElementTree.fromstring(resp.content)

            if root.tag == 'error':
                dv = models.Rate(
                    last_updated=None,
                    value=None,
                    status=models.Success(False, "Could not retrieve data: {}".format(resp.text))
                )
                return dv

        except Exception as e:
            if resp.status_code != 200:
                dv = models.Rate(
                    last_updated=None,
                    value=None,
                    status=models.Success(False, "Could not retrieve data: {}".format(resp.text))
                )
                return dv

        series = root.find('serie')
        ev = series.find('Obs')
        value = ev.find('dato').text
        date_string = ev.find('fecha').text

        # We assume all data from DOF is updated at 12:00, as described in footnote 2 in the exchange rate site
        tzdate = date_string + 'T12:00:00'
        date = datetime.datetime.strptime(tzdate, '%d/%m/%YT%H:%M:%S')

        tz = pytz.timezone('America/Mexico_City')
        tz_date = tz.localize(date)

        dv = models.Rate(
            last_updated=tz_date.isoformat(),
            value=float(value),
            status=models.Success()
        )
        return dv

    @extend_schema(
        request=None,
        responses={
            200: serializers.WrappedRatesSerializer
        }
    )
    def get(self, request, format=None):
        '''
        Fetches latest USD to MXN exchange rate information from [Diario Oficial de la Federación](https://www.banxico.org.mx/tipcamb/tipCamMIAction.do), [Fixer](https://fixer.io/), and [Banxico](https://www.banxico.org.mx/SieAPIRest/service/v1/doc/consultaDatosSerieOp)
        '''

        fr = models.FullRates(
            self.fetch_dof_data(),
            self.fetch_fixer_data(),
            self.fetch_banxico_data()
        )

        wr = models.WrappedRates(fr)

        resp = serializers.WrappedRatesSerializer(wr).data

        return Response(resp)
