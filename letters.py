# -*- coding: utf-8 -*-

import json
from string import ascii_lowercase
import string

_get_letters_cache = None
def _get_letters():
  global _get_letters_cache
  if _get_letters_cache is None:
    _get_letters_cache = json.load(open('letters.json'))
    VOWELLS = set(x for x in 'aeiouy')
    CONSONANTES = set(ascii_lowercase).difference(VOWELLS)
    _get_letters_cache += list(
      [letter, [letter], True] for letter in VOWELLS
    )
    _get_letters_cache += list(
      [letter, [letter], False] for letter in CONSONANTES
    )
  return _get_letters_cache

def is_vowell(letter):
  if type(letter) is not unicode:
    letter = unicode(letter, "utf-8")
  try:
    return next(l[-1] for l in _get_letters() if l[0] == letter)
  except StopIteration:
    raise IndexError(letter)

def to_tipa(letter):
  if type(letter) is not unicode:
    letter = unicode(letter, "utf-8")
  try:
    l = next(l[1][0] for l in _get_letters() if l[0] == letter)
  except StopIteration:
    raise IndexError(letter)
  if len(l) == 4 and l[0] == '\\' and l[-1] == ' ' and (
      l[1] not in string.ascii_lowercase and
      l[1] not in string.ascii_uppercase 
    ):
    l = l[:-1]
  return l

def _safe_index(l, v):
  try:
    return l.index(v)
  except ValueError:
    return None

def to_order_tuple(letter):
  return (
      _safe_index(_VOWEL_ORDER, letter),
      _safe_index(_CONSONANT_ORDER, letter),
      unicode(letter)
  )


_CONSONANT_ORDER = (
  u'pbtdʈɖcɟkɡqɢʔmɱnɳɲŋɴʙrʀⱱɾɽɸβfvθðszʃʒʂʐçʝxɣχʁħʕhɦɬɮʋɹɻjwɥɰlɭʎʟʘǀǃǂǁɓɗʄɠʛʍʜʢ'
  u'ʡɕʑɺɧ'
)

_VOWEL_ORDER = u'iyɨʉɯuɪʏʊeøɘɵɤoɛœɜɞʌɔæɐaɶɑɒə'
