# -*- coding: utf-8 -*-

import unittest

from itertools import izip
from csv_loader import csv_rows
from letters import is_vowell
from word_parsing import (
    BadIPATone,
    InvalidLetter,
    make_letter,
    make_letters,
    make_morpheme,
    make_morphemes,
    make_syllable,
    make_syllables,
    make_word,
    MorphemeMismatch,
    ToneTextSyllableMismatch,
    Word,
)

class TestWordParsing(unittest.TestCase):
  """
  Tests for all of the layers of word parsing.
  """

  def test_letters_split(self):
    for input_text, expected in [
      (u'kɔ', [u'k', u'ɔ']),
      (u'k\~ɔ', [u'k', u'\~ɔ']),
      (u'k^{w}ɔ', [u'k^{w}', u'ɔ']),
      (u'k^{w}\~ɔ', [u'k^{w}', u'\~ɔ']),
    ]:
      self.assertEqual(make_letters(input_text),
                       list(make_letter(x) for x in expected))

  def test_invalid_letters(self):
    self.assertRaises(InvalidLetter, lambda: make_letter('a^{w}'))
    self.assertRaises(InvalidLetter, lambda: make_letter('\~k'))
 
  def test_make_syllables(self):
    self.assertEqual(make_syllables(u'ɟekapip', '1.23.4'),
                     [
                       make_syllable(u'ɟe', u'1'),
                       make_syllable(u'ka', u'23'),
                       make_syllable(u'pip', u'4'),
                     ]
    )
    self.assertEqual(make_syllables(u'o', '1234'),
                     [make_syllable(u'o', u'1234')])

  def test_make_syllables_unequal(self):
    self.assertRaises(
        ToneTextSyllableMismatch,
        lambda: make_syllables(u'cata', '1.23.4')
    )

    self.assertRaises(
        ToneTextSyllableMismatch,
        lambda: make_syllables(u'cata', '1')
    )

  def test_make_morphemes(self):
    self.assertEqual(
        make_morphemes('ku-lala-bi-pod', 'PART-bat-mouse-PART', '1-2.3-4-5'),
        [
          make_morpheme('ku', '1', is_particle=True),
          make_morpheme('lala', '2.3'),
          make_morpheme('bi', '4', is_suffix=True),
          make_morpheme('pod', '5', is_particle=True),
        ]
    )

  def test_make_morphemes_unequal(self):
    """
    Making morphemes out of words within unequal numbers of morphemes is
    invalid.
    """
    self.assertRaises(
        MorphemeMismatch,
        lambda: make_morphemes('a-b', 'c-d', '1-2-3')
    )
    self.assertRaises(
        MorphemeMismatch,
        lambda: make_morphemes('a-b-z', 'c-d', '1-2')
    )
    self.assertRaises(
        MorphemeMismatch,
        lambda: make_morphemes('a-b', 'c-d-e', '1-2')
    )

  def test_bad_word_tone(self):
    """
    Words without well structured tone markings are rejected.
    """
    for x in [
        'cat123',
        'cat^{}',
        'cat^{abc}',
        'cat^1',
        'cat^{1',
        'cat^1}',
        'cat^{a^bc}',
        'cat^{a^bc}^',
    ]:
      self.assertRaises(
          BadIPATone,
          lambda: make_word(x, 'gloss', 'category')
      )

  def test_word_parsing(self):
    """
    Verify that words are correctly parsed into morphemes.
    """
    for parsed, manually in [
        (make_word('koka-nu-po^{12.3-4-56}', 'PART-B-C', 'N'),
          Word(make_morphemes('koka-nu-po', 'PART-B-C', '12.3-4-56'), 'N')),
        (make_word('a^{1}', 'A', 'V'),
          Word(make_morphemes('a', 'A', '1'), 'V')),
        ]:
      self.assertEqual(parsed, manually)

class TestLetters(unittest.TestCase):
  """
  Tests for the letters module.
  """

  def test_is_vowell(self):
    """
    Vowells are vowells.
    """
    self.assertTrue(is_vowell('u'))
    self.assertTrue(is_vowell('a'))
    self.assertTrue(is_vowell('ə'))

  def test_is_not_vowell(self):
    """
    consonants are not vowells
    """
    self.assertFalse(is_vowell('l'))
    self.assertFalse(is_vowell('k'))
    self.assertFalse(is_vowell('ʤ'))

  def test_is_not_letter(self):
    """
    Unknown letters throw an error.
    """
    self.assertRaises(IndexError, lambda: is_vowell('cat'))
    self.assertRaises(IndexError, lambda: is_vowell('9'))
    self.assertRaises(IndexError, lambda: is_vowell(''))


class TestCSVLoader(unittest.TestCase):
  """
  Tests for the CSV loader.
  """

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

  def test_loads_test_data(self):
    for observed, expected in izip(csv_rows('./test_data.csv'),
                                   self.TEST_FILE_DATA):
      self.assertEqual(observed, expected)

if __name__ == '__main__':
    unittest.main()

