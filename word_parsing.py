
from itertools import izip_longest, islice
import re

from letters import is_vowell, to_tipa

class WordParseError(Exception):
  pass

class Word(object):

  def __init__(self, morphemes, syllables, category):
    self._morphemes = tuple(morphemes)
    self._syllables = tuple(syllables)
    self._category = category

  def __eq__(self, other):
    return (
        self._morphemes == other._morphemes and
        self._syllables == other._syllables and
        self._category == other._category
    )

  def __ne__(self, other):
    return not self == other

  def __repr__(self):
    return '<Word(%s, %s, %s)>' % (
        repr(self._morphemes), repr(syllables), repr(self._category))

  def __hash__(self):
    return hash((self._morphemes, self._syllables, self._category))

  @property
  def category(self):
    return self._category
  
  def iter_morphemes(self):
    for m in self._morphemes:
      yield m

  def iter_syllables(self):
    for s in self._syllables:
      yield s


class Morpheme(object):

  def __init__(self, letters, gloss, is_particle=False, is_suffix=False):
    self._letters = tuple(letters)
    self._gloss = gloss
    self._is_particle = is_particle
    self._is_suffix = is_suffix

  def __eq__(self, other):
    return (
        self._letters == other._letters and 
        self._gloss == other._gloss and 
        self._is_particle == other._is_particle and 
        self._is_suffix == other._is_suffix
    )

  def __hash__(self):
    return hash((
      self._letters,
      self._gloss,
      self._is_particle,
      self._is_suffix,
    ))

  def __ne__(self, other):
    return not self == other

  def __repr__(self):
    return u'<Morpheme(%s, %s)>' % (repr(list(
        token for flag, token in [(self._is_suffix, 'suffix'),
                                  (self._is_particle, 'particle')]
        if flag
      )), repr(self._letters))

  def iter_letters(self):
    for l in self._letters:
      yield l


class SyllablesMustHaveVowells(WordParseError):
  pass


class Syllable(object):

  def __init__(self, letters, tone):
    self._letters = letters
    self._tone = tone
    if not self.has_vowell():
      raise SyllablesMustHaveVowells(
          'Sylable %s with tone %s does not have a vowell' % (
            self._letters, self._tone))

  def __eq__(self, other):
    return (
        self._letters == other._letters and 
        self._tone == other._tone
    )

  def __ne__(self, other):
    return not self == other

  def letters(self):
    """
    Returns a tuple of the letters in this syllable.
    """
    return tuple(self._letters)

  @property
  def tone(self):
    return self._tone

  def __hash__(self):
    return hash((
      self.letters(), self._tone
    ))

  def __repr__(self):
    return u'<Syllable(%s, %s)>' % (repr(self._letters), repr(self._tone))
  
  def has_vowell(self):
    return any(l.is_vowell() for l in self._letters)

  def iter_letters(self):
    for l in self._letters:
      yield l

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
    if text == 'r':
      self._text = 'l'
    self._is_nasal = is_nasal
    self._is_labialized = is_labialized
    self._is_long = is_long

    if (is_nasal or is_long) and not self.is_vowell():
      raise InvalidLetter('Nasal letters must be vowells (%s)' % repr(self))

    if is_labialized and self.is_vowell():
      raise InvalidLetter('Letters with a w must be consonants (%s)' %
                          repr(self))

  @property
  def is_nasal(self):
    return self._is_nasal

  def is_vowell(self):
    try:
      return is_vowell(self._text)
    except IndexError as e:
      raise InvalidLetter(
          "Unknown letter when determining if something was a vowell: '%s'" %
          e.args[0]
      )

  def to_tipa(self):
    return '%s%s%s' % (
        self._nasal_prefix(), to_tipa(self._text), self._suffix())

  def __eq__(self, other):
    if type(self) != type(other):
      return NotImplemented
    return (
        self._text == other._text and 
        self._is_labialized == other._is_labialized and 
        self._is_nasal == other._is_nasal and 
        self._is_long == other._is_long
    )

  def __lt__(self, other):
    if self._text < other._text:
      return True
    if not self._is_nasal and other._is_nasal:
      return True
    if not self._is_labialized and other._is_labialized:
      return True
    if not self._is_long and other._is_long:
      return True
    return False

  def __le__(self, other):
    return self == other or self < other

  def __gt__(self, other):
    return not self <= other

  def __ge__(self, other):
    return not self < other

  def __ne__(self, other):
    return not self == other

  def __hash__(self):
    return hash((
      self._text, self._is_labialized, self._is_nasal, self._is_long
    ))

  def _nasal_prefix(self):
    if self._is_nasal:
      return '\\~'
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

def make_morpheme(text, gloss, is_particle=False, is_suffix=False):
  return Morpheme(
      make_letters(text),
      gloss,
      is_particle=is_particle,
      is_suffix=is_suffix
  )

class MorphemeMismatch(WordParseError):
  pass

def make_morphemes(texts, glosses):
  results = []
  have_root = False
  for text, gloss in izip_longest(
      texts.split('-'), glosses.split('-')):
    if text is None or gloss is None:
      raise MorphemeMismatch(
        'Could not divide into morphemes text(%s), gloss(%s)' % (
          texts, glosses)
      )
    part = (gloss=="PART")
    suffix = have_root and not part
    morpheme_gloss = gloss
    if part:
      morpheme_gloss = None
    results.append(make_morpheme(
      text, morpheme_gloss, is_particle=part, is_suffix=suffix
    ))
    have_root = have_root or not part

  return results


class BadIPATone(WordParseError):
  pass

def make_word(ipa, gloss, category):
  if not re.match(r'.*\^\{[0-9.-]+\}$', ipa):
    raise BadIPATone("Could not extract tone from ipa(%s)" % repr(ipa))
  breakpoint = ipa.rfind('^')
  text = ipa[:breakpoint]
  tone = ipa[breakpoint+2:-1].replace('-', '.')
  return Word(
      make_morphemes(text, gloss),
      make_syllables(text.replace('-', ''), tone),
      category
  )
