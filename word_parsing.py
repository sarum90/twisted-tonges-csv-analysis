
from itertools import izip_longest, islice
import re

from letters import is_vowell

class WordParseError(Exception):
  pass

class Word(object):

  def __init__(self, morphemes, category):
    self._morphemes = morphemes
    self._category = category

  def __eq__(self, other):
    return (
        self._morphemes == other._morphemes and
        self._category == other._category
    )

  def __repr__(self):
    return '<Word(%s, %s)>' % (repr(self._morphemes), repr(self._category))


class Morpheme(object):

  def __init__(self, syllables, is_particle=False, is_suffix=False):
    self._syllables = syllables
    self._is_particle = is_particle
    self._is_suffix = is_suffix

  def __eq__(self, other):
    return (
        self._syllables == other._syllables and 
        self._is_particle == other._is_particle and 
        self._is_suffix == other._is_suffix
    )

  def __repr__(self):
    return u'<Morpheme(%s, %s)>' % (repr(list(
        token for flag, token in [(self._is_suffix, 'suffix'),
                                  (self._is_particle, 'particle')]
        if flag
      )), repr(self._syllables))


class Syllable(object):

  def __init__(self, letters, tone):
    self._letters = letters
    self._tone = tone

  def __eq__(self, other):
    return (
        self._letters == other._letters and 
        self._tone == other._tone
    )

  def __repr__(self):
    return u'<Syllable(%s, %s)>' % (repr(self._letters), repr(self._tone))
  
  def has_vowell(self):
    return any(l.is_vowell() for l in self._letters)

class InvalidLetter(WordParseError):
  pass

class Letter(object):
  """
  Represents a single IPA letter.

  Has the logic built-in to determine if it is or is not a vowell.

  This is tracked as a single unicode character, and some bits that mark nasal,
  labialized, and long-vowell diacritics.
  """
  
  def __init__(self, text, is_nasal, is_labialized, is_long):
    if is_nasal and is_labialized:
      raise InvalidLetter('Cannot be both nasal and have a raised w')
    self._text = text
    self._is_nasal = is_nasal
    self._is_labialized = is_labialized
    self._is_long = is_long

    if (is_nasal or is_long) and not self.is_vowell():
      raise InvalidLetter('Nasal letters must be vowells (%s)' % repr(self))

    if is_labialized and self.is_vowell():
      raise InvalidLetter('Letters with a w must be consonants (%s)' %
                          repr(self))

  def is_vowell(self):
    return is_vowell(self._text)

  def __eq__(self, other):
    return (
        self._text == other._text and 
        self._is_labialized == other._is_labialized and 
        self._is_nasal == other._is_nasal and 
        self._is_long == other._is_long
    )

  def _nasal_prefix(self):
    if self._is_nasal:
      return '/~'
    return ''

  def _suffix(self):
    if self._is_long:
      return ':'
    if self._is_labialized:
      return '^{w}'
    return ''

  def text(self):
    return u'%s%s%s' % (self._nasal_prefix(),
                        self._text,
                        self._suffix())

  def __repr__(self):
    return u'<Letter %s>' % repr(self.text())

_NASAL = '\~'
_LONG = ':'
_LABIALIZED = '^{w}'
_NASAL_SUFFIX_1 = '^~'
_NASAL_SUFFIX_2 = '^{~}'
_NASAL_SUFFIX_3 = '~'

def make_letter(text):
  is_labialized = False
  is_nasal = False
  is_long = False
  if text.startswith(_NASAL):
    text = text[len(_NASAL):]
    is_nasal = True
  if text.endswith(_LABIALIZED):
    text = text[:-len(_LABIALIZED)]
    is_labialized = True
  if text.endswith(_LONG):
    text = text[:-len(_LONG)]
    is_long = True
  if text.endswith(_NASAL_SUFFIX_1):
    text = text[:-len(_NASAL_SUFFIX_1)]
    is_nasal = True
  if text.endswith(_NASAL_SUFFIX_2):
    text = text[:-len(_NASAL_SUFFIX_2)]
    is_nasal = True
  if text.endswith(_NASAL_SUFFIX_3):
    text = text[:-len(_NASAL_SUFFIX_3)]
    is_nasal = True
  return Letter(text, is_nasal, is_labialized, is_long)

def _clean_text(text):
  processed_text = text
  for removed_letter in u'() \xa0':
    processed_text = processed_text.replace(removed_letter, '')
  return processed_text

def make_letters(text):
  result = []
  processed_text = _clean_text(text)
  while processed_text:
    split = 1
    if processed_text.startswith(_NASAL):
      split = len(_NASAL)+1

    letter = processed_text[:split]
    rest = processed_text[split:]

    for suffix in [
        _NASAL_SUFFIX_1,
        _NASAL_SUFFIX_2,
        _NASAL_SUFFIX_3,
        _LABIALIZED,
        _LONG
    ]:
      if rest.startswith(suffix):
        letter += rest[:len(suffix)]
        rest = rest[len(suffix):]

    result.append(make_letter(letter))
    processed_text = rest
  return result


def make_syllable(text, tone):
  return Syllable(make_letters(text), unicode(tone))


def _syllable_letter_grouper(letters):
  """
  Takes a list of letters, and generates sub-lists of letters that are
  valid syllables.

  The algorithm is:

  1) If there is only 1 vowell left in the remaining letters, return all
     remaining letters.
  2) Otherwise return all remaining letters until the first vowell.

  :param letters: A list of Letter instances.

  :yields: Lists of letters, 1 per syllable.
  """
  vowell_count = sum(1 for l in letters if l.is_vowell())
  letter_iterator = iter(letters)
  while vowell_count > 1:
    next_chunk = []
    while True:
      c = next(letter_iterator)
      next_chunk.append(c)
      if c.is_vowell():
        break
    vowell_count -= 1
    yield next_chunk
  yield list(x for x in letter_iterator)


class ToneTextSyllableMismatch(WordParseError):
  pass


def _raise(ex):
  raise ex


def _count_syllables(text):
  x = list(_syllable_letter_grouper(make_letters(text)))
  if len(x) != 1:
    return len(x)
  if any(l.is_vowell() for l in x[0]):
    return 1
  return 0


def make_syllables(text, tones):
  letters = make_letters(text)

  return list(
    Syllable(letters, unicode(tone))
    if letters is not None and tone is not None
    else _raise(ToneTextSyllableMismatch(
      'Unequal number of syllables in text(%s) and tone(%s).' % (repr(text),
                                                                 repr(tones))
    ))
    for letters, tone in izip_longest(
      _syllable_letter_grouper(letters),
      tones.split('.')
    )
  )

def make_morpheme(text, tone, is_particle=False, is_suffix=False):
  return Morpheme(
      make_syllables(text, tone),
      is_particle=is_particle,
      is_suffix=is_suffix
  )

class MorphemeMismatch(WordParseError):
  pass

def make_morphemes(texts, glosses, tones):
  results = []
  have_root = False
  tone_iter = iter(tones.split('.'))
  for text, gloss in izip_longest(
      texts.split('-'), glosses.split('-')):
    if text is None or gloss is None:
      raise MorphemeMismatch(
        'Could not divide into morphemes text(%s), gloss(%s), tone(%s)' % (
          texts, glosses, tones)
      )
    tone = '.'.join(list(islice(tone_iter, _count_syllables(text))))
    part = (gloss=="PART")
    suffix = have_root and not part
    results.append(make_morpheme(text, tone, part, suffix))
    have_root = have_root or not part

  if next(tone_iter, None) is None:
    return results
  raise MorphemeMismatch(
    'Could not divide into morphemes text(%s), gloss(%s), tone(%s)' % (
      texts, glosses, tones)
  )

class BadIPATone(WordParseError):
  pass

def make_word(ipa, gloss, category):
  if not re.match(r'.*\^\{[0-9.]+\}$', ipa):
    raise BadIPATone("Could not extract tone from ipa(%s)" % repr(ipa))
  breakpoint = ipa.rfind('^')
  text = ipa[:breakpoint]
  tone = ipa[breakpoint+2:-1]
  return Word(make_morphemes(text, gloss, tone), category)
