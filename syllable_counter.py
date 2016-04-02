
class SyllableCounter(object):

  def __init__(self, syllable_counts, vowells, consonants):
    self._syllable_counts = syllable_counts
    self._vowells = sorted(list(vowells))
    self._consonants = sorted(list(consonants))
    self._vowell_count_cache = {}
    self._consonant_count_cache = {}
    self._total_count = None

  def iter_vowells(self):
    for v in self._vowells:
      yield v

  def iter_consonants(self):
    for c in self._consonants:
      yield c

  def syllable_count(self, syllable):
    return self._syllable_counts.get(syllable, 0)

  def syllable_with_vowell_count(self, vowell):
    if vowell not in self._vowell_count_cache:
      self._vowell_count_cache[vowell] = sum(
        self.syllable_count(c + vowell) for c in self.iter_consonants()
      )
    return self._vowell_count_cache[vowell]


  def syllable_with_consonant_count(self, consonant):
    if consonant not in self._consonant_count_cache:
      self._consonant_count_cache[consonant] = sum(
        self.syllable_count(consonant + v) for v in self.iter_vowells()
      )
    return self._consonant_count_cache[consonant]
  
  def total_count(self):
    if self._total_count is None:
      self._total_count = sum(
          self.syllable_with_vowell_count(v) for v in self.iter_vowells()
      )
    return self._total_count

