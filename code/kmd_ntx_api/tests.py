#!/usr/bin/env python3
import pytest
import requests
from django.urls import reverse, get_resolver
from django.test import TestCase
from django.conf import settings

from kmd_ntx_api.cache_data import navigation_cache

base_url = 'http://stats.kmd.io'
if settings.DEBUG:
    base_url = 'http://116.203.120.91:8762'


def get_urls_list(server='dev'):
    urls = []
    nav = navigation_cache()
    for section in nav:
        for option in nav[section]['options']:
            urls.append(nav[section]['options'][option]['url'])
    return urls


class TestUrls(TestCase):
    def test_navigation(self):
        urls = get_urls_list()
        for url in urls:
            resp = requests.get(f'{base_url}/{url}')
            self.assertEqual(resp.status_code, 200)

    def test_static_pages(self):
        urls = get_resolver(None).reverse_dict.keys()
        for url in urls:
            url = reverse(url)
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
