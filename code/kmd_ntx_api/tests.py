#!/usr/bin/env python3
import pytest
import requests
from django.urls import reverse, get_resolver
from django.test import TestCase
from django.conf import settings

from .navigation import NAV_DATA

base_url = 'http://stats.kmd.io'
if settings.DEBUG:
    base_url = 'http://116.203.120.91:8762'

def get_urls_list(server='dev'):
    urls = []
    for section in NAV_DATA:
        for option in NAV_DATA[section]['options']:
            urls.append(NAV_DATA[section]['options'][option]['url'])
    return urls


class TestUrls(TestCase):
    def test_navigation(self):
        urls = get_urls_list()
        for url in urls:
            r = requests.get(f'{base_url}/{url}')
            self.assertEqual(resp.status_code, 200)

    def test_static_pages(self):
        urls = get_resolver(None).reverse_dict.keys()
        print(urls)
        for url in urls:
            url = reverse(url)
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
