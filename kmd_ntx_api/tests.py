from django.test import TestCase

# Create your tests here.

from helper_lib import *
from table_lib import *
from query_lib import *
from info_lib import *

class Test_helper_lib(TestCase):

    def test_lil_endian(self):
        hex_str = "efbeadde"
        actual = lil_endian(hex_str)
        expected = "deadbeef"
        self.assertEqual(actual, expected)

    def test_day_hr_min_sec(self):
        seconds = 6
        actual = day_hr_min_sec(seconds, 2)
        expected = "6 sec"
        self.assertEqual(actual, expected)
        seconds = 66
        actual = day_hr_min_sec(seconds, 1)
        expected = "1 min"
        self.assertEqual(actual, expected)
        seconds = 66
        actual = day_hr_min_sec(seconds, 2)
        expected = "1 min, 6 sec"
        self.assertEqual(actual, expected)
        seconds = 86466
        actual = day_hr_min_sec(seconds, 2)
        expected = "1 day, 0 hr"
        self.assertEqual(actual, expected)
        seconds = 86466
        actual = day_hr_min_sec(seconds, 2)
        expected = "1 day, 0 hr, 1 min, 6 sec"
        self.assertEqual(actual, expected)

if __name__ == '__main__':
        main(exit=False)