import unittest

import statsloaderx

class StatsLoaderTest(unittest.TestCase):

    def test_get_last_page(self):
        print statsloaderx.get_last_page(1, 1)

    def test_get_user_name(self):
        self.assertEqual(statsloaderx.get_user_name(0), u'Guest User')