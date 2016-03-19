# -*- coding: utf-8 -*-

import unittest

from itertools import izip
from csv_loader import csv_rows

TEST_FILE_DATA = [
  {"IPA": u"li^{3}","Gloss": "eat", "Category": "V", "Text": "",
   "count": "29"},
  {"IPA": u"kɔk^{w}ɪ^{2.3}","Gloss": "chicken", "Category": "N", "Text": "",
   "count": "1"},
  {"IPA": u"li^{4}","Gloss": "songs", "Category": "N", "Text": "",
   "count": "1"},
  {"IPA": u"si^{3}","Gloss": "trees", "Category": "N", "Text": "",
   "count": "6"},
  {"IPA": u"siə^{3}","Gloss": "laugh", "Category": "V", "Text": "",
   "count": "1"},
  {"IPA": u"cɛ-li^{2.2}","Gloss": "write-NMLZ", "Category": "N", "Text": "",
   "count": "1"},
  {"IPA": u"cɛ-ɲɔ^{2.2}","Gloss": "write-AGT", "Category": "N", "Text": "",
   "count": "1"},
  {"IPA": u"bəle^{2.2}","Gloss": "sing", "Category": "V", "Text": "",
   "count": "1"},
  {"IPA": u"ɟe-je^{42.3}","Gloss": "egg-SG", "Category": "N", "Text": "",
   "count": "3"},
]

class TestCSVLoader(unittest.TestCase):

  def test_loads_test_data(self):
    for observed, expected in izip(csv_rows('./test_data.csv'),
                                   TEST_FILE_DATA):
      self.assertEqual(observed, expected)

if __name__ == '__main__':
    unittest.main()

