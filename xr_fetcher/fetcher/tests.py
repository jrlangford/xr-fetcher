import json
import unittest
from unittest import mock
import re
from datetime import datetime, timedelta

from django.utils import timezone
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.cache import cache

from rest_framework.test import force_authenticate, APIRequestFactory
from rest_framework.test import APITestCase, APIClient
from oauth2_provider.models import Application, AccessToken

from . import views, scraper

def get_html_file(path, encoding):
    import codecs
    import sys

    from bs4 import BeautifulSoup
    f = codecs.open(path, "r", encoding)
    return f.read()

# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, content, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.content = content

        def json(self):
            return self.json_data

    if args[0] == settings.DOF_SCRAPE_URL:
        html = get_html_file("xr_fetcher/fetcher/resources/SIE-Mercado_cambiario.html", "windows-1252")
        return MockResponse("", html, 200)
    elif args[0].startswith(settings.FIXER_BASE_URL + 'latest'):
        # extract access_key
        m = re.search('[^\?]+\?(.*)?', args[0])
        params = {}
        if m:
            query_string = m.group(1)
            vals = query_string.split('&')
            for v in vals:
                p = v.split('=')
                params[p[0]]=p[1]

        if params['access_key']=="":
            fixer_mock_err_response = {
                "success": False,
                "error": {
                    "code": 101,
                    "type": "missing_access_key",
                    "info": "You have not supplied an API Access Key. [Required format: access_key=YOUR_ACCESS_KEY]"
                }
            }
            return MockResponse(fixer_mock_err_response, "", 200)

        fixer_mock_response = {
            "success": True,
            "timestamp": 1605521261,
            "base": params['base'],
            "date": "2020-11-16",
            "rates": {
                params['symbols']: 20.5303
            }
        }
        return MockResponse(fixer_mock_response, "", 200)
    if args[0] == settings.BANXICO_BASE_URL + 'series/SF43718/datos/oportuno?mediaType=xml':
        xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><series><serie idSerie="SF43718" titulo="Tipo de cambio Pesos por d\xc3\xb3lar E.U.A. Tipo de cambio para solventar obligaciones denominadas en moneda extranjera Fecha de determinaci\xc3\xb3n (FIX)"><Obs><dato>20.4833</dato><fecha>13/11/2020</fecha></Obs></serie></series>'
        return MockResponse("", xml, 200)

    return MockResponse(None, 404)


class FetcherTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.fetchRates = views.FetchRates.as_view()

        self.test_user = get_user_model().objects.create_user("test_user", "test@user.com", "123456")
        self.application = Application(
            name="Test Application",
            redirect_uris="http://localhost",
            user=self.test_user,
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
        )
        self.application.save()

        from datetime import datetime, timedelta
        from django.utils import timezone

        self.tok = AccessToken.objects.create(
            user=self.test_user, token='1234567890',
            application=self.application, scope='read',
            expires=timezone.now() + timedelta(days=1)
        )

    def tearDown(self):
            # We clear the cache to reset any throttling counters affected by these tests.
            cache.clear()

    def test_scrape_local(self):
        html = get_html_file("xr_fetcher/fetcher/resources/SIE-Mercado_cambiario.html", "windows-1252")

        data = scraper.scrapeHTML(html)

        self.assertEquals(data['date'], "15/11/2020")
        self.assertEquals(data['value'], 20.5303)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_rates(self, mock_get):
        request = self.factory.get('/api/v0/rates/')
        force_authenticate(request, user=self.test_user, token=self.tok)
        response = self.fetchRates(request)

        self.assertIs(response.status_code, 200)

        self.assertEqual(response.data['rates']['dof']['status']['success'], True)
        self.assertEqual(response.data['rates']['dof']['last_updated'], '2020-11-15T12:00:00-06:00')
        self.assertEqual(response.data['rates']['dof']['value'], 20.5303)

        self.assertEqual(response.data['rates']['fixer']['status']['success'], True)
        self.assertEqual(response.data['rates']['fixer']['last_updated'], '2020-11-16T10:07:41+00:00')
        self.assertEqual(response.data['rates']['fixer']['value'], 20.5303)

        self.assertEqual(response.data['rates']['banxico']['status']['success'], True)
        self.assertEqual(response.data['rates']['banxico']['value'], 20.4833)
        self.assertEqual(response.data['rates']['banxico']['last_updated'], '2020-11-13T12:00:00-06:00')

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_rates_no_api_keys(self, mock_get):
        request = self.factory.get('/api/v0/rates/')
        force_authenticate(request, user=self.test_user, token=self.tok)

        response = None

        with self.settings(FIXER_API_ACCESS_KEY='', BANXICO_TOKEN=''):
            response = self.fetchRates(request)

        self.assertIs(response.status_code, 200)

        self.assertEqual(response.data['rates']['dof']['value'], 20.5303)

        self.assertEqual(response.data['rates']['fixer']['status']['success'], False)
        self.assertEqual(response.data['rates']['banxico']['status']['success'], False)

class ThrottleTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.fetchRates = views.FetchRates.as_view()

        self.test_user = get_user_model().objects.create_user("test_user", "test@user.com", "123456")
        # App and token setup for App 1
        self.application = Application(
            name="Test Application",
            redirect_uris="http://localhost",
            user=self.test_user,
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
        )
        self.application.save()

        # App and token setup for App 2
        self.application2 = Application(
            name="Test Application",
            redirect_uris="http://localhost",
            user=self.test_user,
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
        )
        self.application2.save()

        self.tok2 = AccessToken.objects.create(
            user=self.test_user, token='1234567890',
            application=self.application2, scope='read',
            expires=timezone.now() + timedelta(days=1)
        )

    def tearDown(self):
            # We clear the cache to reset any throttling counters affected by these tests.
            cache.clear()

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_reject_1(self, mock_get):
        client = APIClient()
        apps = [self.application, self.application2]
        for app in apps:

            token = AccessToken.objects.create(
                user=self.test_user, token="1234567890_{}".format(app.id),
                application=app, scope='read',
                expires=timezone.now() + timedelta(days=1)
            )

            client.force_authenticate(user=self.test_user, token=token)

            url = '/api/v0/rates/'

            testing_threshold = 5
            THRESHOLD_STRING = "{}/min".format(testing_threshold)

            REST_FRAMEWORK_OVERRIDE=settings.REST_FRAMEWORK
            REST_FRAMEWORK_OVERRIDE['DEFAULT_THROTTLE_RATES']['oauth_application'] = THRESHOLD_STRING

            with self.settings(REST_FRAMEWORK=REST_FRAMEWORK_OVERRIDE):
                for i in range(0, testing_threshold):
                    response = client.get(url)
                    self.assertEqual(response.status_code, 200)

                response = client.get(url)
                # 429 - too many requests
                self.assertEqual(response.status_code, 429)
