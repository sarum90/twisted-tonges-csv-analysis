

import json
from string import ascii_lowercase

_get_letters_cache = None
def _get_letters():
  global _get_letters_cache
  if _get_letters_cache is None:
    _get_letters_cache = json.load(open('letters.json'))
    VOWELLS = set(x for x in 'aeiouy')
    CONSONANTES = set(ascii_lowercase).difference(VOWELLS)
    _get_letters_cache += list(
      [letter, True] for letter in VOWELLS
    )
    _get_letters_cache += list(
      [letter, False] for letter in CONSONANTES
    )
  return _get_letters_cache

def is_vowell(letter):
  if type(letter) is not unicode:
    letter = unicode(letter, "utf-8")
  try:
    return next(l[-1] for l in _get_letters() if l[0] == letter)
  except StopIteration:
    raise IndexError(letter)
