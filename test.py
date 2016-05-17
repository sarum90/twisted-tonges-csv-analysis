# -*- coding: utf-8 -*-

import unittest

from itertools import izip
from csv_loader import csv_rows
from letters import is_vowell
from analyse import tones_to_melody
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
    SyllablesMustHaveVowells,
    ToneTextSyllableMismatch,
    Word,
)

class TestWordParsing(unittest.TestCase):
  """
  Tests for all of the layers of word parsing.
  """

  def test_tones_to_melody(self):
    """
    Duplicate adjacent tones are be removed to become melodies.
    """
    self.assertEqual(tones_to_melody('112233'), '123')
    self.assertEqual(tones_to_melody(''), '')
    self.assertEqual(tones_to_melody('12322'), '1232')
    self.assertEqual(tones_to_melody('11'), '1')

  def test_letter_keys(self):
    a = {}
    a[make_letter('l')] = 0
    a[make_letter('l')] += 1
    a[make_letter('l')] += 1
    self.assertEqual(a[make_letter('l')], 2)

  def test_letters_split(self):
    for input_text, expected in [
      (u'kɔ', [u'k', u'ɔ']),
      (u' k\~ɔ', [u'k', u'\~ɔ']),
      (u'kɔ^~', [u'k', u'\~ɔ']),
      (u'kɔ^{~}', [u'k', u'\~ɔ']),
      (u'kɔ~', [u'k', u'\~ɔ']),
      (u'k^{w} ɔ', [u'k^{w}', u'ɔ']),
      (u'k^{w}(\~ɔ)', [u'k^{w}', u'\~ɔ']),
      (u'k^{w}ɔ:', [u'k^{w}', u'ɔ:']),
      (u'kpa', [u'kp', u'a']),
      (u'kba', [u'k', u'b', u'a']),
      (u'gba', [u'gb', u'a']),
      (u'gpa', [u'g', u'p', u'a']),
    ]:
      self.assertEqual(make_letters(input_text),
                       list(make_letter(x) for x in expected))
    for input_text, expected in [
      (u'k\~ɔ', [u'k', u'ɔ']),
      (u' k^{w}ɔ', [u'k', u'ɔ']),
      (u'\tk^{w}\~ɔ', [u'k', u'ɔ']),
      (u'k^{w}ɔ:', [u'k^{w}', u'ɔ']),
    ]:
      self.assertNotEqual(make_letters(input_text),
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

  def test_syllable_keys(self):
    a = {}
    a[make_syllable(u'ɟe', u'1')] = 0
    a[make_syllable(u'ɟe', u'1')] += 1
    a[make_syllable(u'ɟe', u'1')] += 1
    self.assertEqual(a[make_syllable(u'ɟe', u'1')], 2)

  def test_syllable_must_have_vowell(self):
    self.assertRaises(
        SyllablesMustHaveVowells,
        lambda: make_syllable('l', '1')
    )

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
        make_morphemes('ku-lala-bi-pod', 'PART-bat-mouse-PART'),
        [
          make_morpheme('ku', None, is_particle=True),
          make_morpheme('lala', 'bat'),
          make_morpheme('bi', 'mouse', is_suffix=True),
          make_morpheme('pod', None, is_particle=True),
        ]
    )

    self.assertEqual(
        make_morphemes('la-bp-o', 'PART-bat-log'),
        [
          make_morpheme('la', None, is_particle=True),
          make_morpheme('bp', 'bat'),
          make_morpheme('o', 'log', is_suffix=True),
        ]
    )

  def test_make_morphemes_unequal(self):
    """
    Making morphemes out of words within unequal numbers of morphemes is
    invalid.
    """
    self.assertRaises(
        MorphemeMismatch,
        lambda: make_morphemes('a-b-z', 'c-d')
    )
    self.assertRaises(
        MorphemeMismatch,
        lambda: make_morphemes('a-b', 'c-d-e')
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

  def test_word_complete_morphemes(self):
    for parsed, manually in [
          (
            make_word('koka-n-o^{12.3.4}', 'A-B-C', 'N'),
            [(make_morpheme('koka', 'A'),
              tuple(make_syllables('koka', '12.3')))]
          ),
          (
            make_word('bo^{1}', 'A', 'N'),
            [(make_morpheme('bo', 'A'),
              tuple(make_syllables('bo', '1')))]
          ),
          (
            make_word('b-o-kana-p-o^{1.2.2.3}', 'PART-PART-C-D-E', 'N'),
            [(make_morpheme('kana', 'C'),
              tuple(make_syllables('kana', '2.2')))]
          ),
          (
            make_word('b-o-p-o^{1.2}', 'PART-A-B-C', 'N'),
            []
          ),
    ]:
      self.assertEqual(list(parsed.iter_complete_morphemes()), manually)

  def test_word_parsing(self):
    """
    Verify that words are correctly parsed into morphemes.
    """
    for parsed, manually in [
        (
          make_word('koka-nu-po^{12.3.4.56}', 'PART-B-C', 'N'),
          Word(
            make_morphemes('koka-nu-po', 'PART-B-C'),
            make_syllables('kokanupo', '12.3.4.56'),
            'N')
          ),
        (
          make_word('a^{1}', 'A', 'V'),
          Word(
            make_morphemes('a', 'A'),
            make_syllables('a', '1'),
            'V'
          )
        ),
        ]:
      self.assertEqual(parsed, manually)

  def test_word_dict_key(self):
    """
    Words can be dictionary keys.
    """
    b = dict()
    b[make_word('koka-nu-po^{12.3.4.56}', 'PART-B-C', 'N')] = 1
    b[make_word('koka-nu-po^{12.3.4.56}', 'PART-B-C', 'N')] += 1
    b[make_word('koke-nu-po^{12.3.4.56}', 'PART-B-C', 'N')] = 1
    self.assertEqual(
          b[make_word('koka-nu-po^{12.3.4.56}', 'PART-B-C', 'N')], 2)
    self.assertEqual(
          b[make_word('koke-nu-po^{12.3.4.56}', 'PART-B-C', 'N')], 1)

  def test_word_equality(self):
    """
    Verify that words are correctly parsed into morphemes.
    """
    for a, b in [
        (make_word('koka-nu-po^{12.3.4.56}', 'PART-B-C', 'N'),
         make_word('koka-nu-po^{12.3.4.65}', 'PART-B-C', 'N'))
    ]:
      self.assertNotEqual(a, b)

    for a, b in [
        (make_word('koka-nu-po^{12.3.4.56}', 'PART-B-C', 'N'),
         make_word('koka-nu-po^{12.3.4.65}', 'PART-B-C', 'N'))
    ]:
      self.assertNotEqual(a, b)

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
    self.assertFalse(is_vowell('kp'))
    self.assertFalse(is_vowell('gb'))

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

