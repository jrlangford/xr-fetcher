import json
import unittest
from unittest import mock

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework.test import force_authenticate, APIRequestFactory
from oauth2_provider.models import Application, AccessToken

from . import views, scraper

class HelloTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.helloView = views.HelloWorld.as_view()

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
            application=self.application, scope='read write',
            expires=timezone.now() + timedelta(days=1)
        )

    def test_hi(self):
        request = self.factory.get('hello/')
        force_authenticate(request, user=self.test_user, token=self.tok)
        response = self.helloView(request)

        self.assertIs(response.status_code, 200)
        self.assertEquals(response.data["message"], "Hello, world!")


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
        self.assertNotEqual(response.data['rates']['dof'], None)
