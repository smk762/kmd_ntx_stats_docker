from django.core.urlresolvers import reverse
from django.test import TestCase
from django.core.urlresolvers import get_resolver


class WebPagesTests(TestCase):

    def test_static_pages(self):
        urls = get_resolver(None).reverse_dict.keys()
        print(urls)
        for url in urls:
            url = reverse(url)
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)

if __name == '__main__':
    test_static_pages(self)