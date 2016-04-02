#/usr/bin/env python

import sys
import os
from itertools import izip
import itertools
from collections import defaultdict
from csv_loader import csv_rows
from word_parsing import (make_word, WordParseError)
from syllable_counter import SyllableCounter

def load_word_counts(filename):
  """
  Reads in a file and returns a dictionary of words mapped to counts.
  """
  raw_rows = csv_rows(filename)
  word_counts = defaultdict(lambda: 0)

  for line_number, raw_row in enumerate(raw_rows, 2):
    count = int(raw_row["count"])
    ipa = raw_row["IPA"]
    if '*' in ipa:
      continue

    # Fixes random badness.. hopefully doesn't hide anything?
    mod_ipa = ipa.replace('(', '').replace(')', '')

    # Work around a passage with an error in it:
    gloss = raw_row["Gloss"] or raw_row["Text"]

    category = raw_row["Category"]

    skipword_characters = {'?'}
    try:
      for i, g in izip(mod_ipa.split('/'), gloss.split('/')):
        word = make_word(i, g, category)
        word_counts[word] += count
    except WordParseError as e:
      print (u"Error on line %d: %s [%s || %s]" %
          (line_number, repr(e), ipa, gloss)).encode('utf-8')
    except IndexError as e:
      unknown_index = e.args[0]
      if unknown_index in skipword_characters:
        print (u"Bad char on line %d: %s [%s || %s]" %
            (line_number, repr(e), ipa, gloss)).encode('utf-8')
      else:
        print "FATAL ERROR ON LINE %d" % line_number
        raise
    except:
      print "FATAL ERROR ON LINE %d" % line_number
      raise
  return word_counts


def iter_clusters(letter_iter):
  """
  Turns an iterator of letters into an iterator of "clusters" where a cluster
  is defined as a list of consecutive consonants or a single vowell.
  """
  consonants = []
  for letter in letter_iter:
    if letter.is_vowell():
      if consonants:
        yield tuple(consonants)
        consonants = []
      yield tuple([letter])
    else:
      consonants.append(letter)
  if consonants:
    yield tuple(consonants)


def print_table(rows):
  for r in rows:
    print u'\t'.join(r).encode('utf-8')

def make_tabular(rows):
  output_rows = []
  rows_iter = iter(rows)
  rows_iter, leading_rows_iter = itertools.tee(rows_iter)
  next(leading_rows_iter)
  double_iter = itertools.izip(rows_iter, leading_rows_iter)
  first_row, _ = next(double_iter)

  output_rows.append(u'\\begin{tabular}{%s}' % u'|'.join(
    (u'l|',) + tuple(u'l' for _ in xrange(len(first_row)-2)) + (u'|l',))
  )
  output_rows.append(u'%s \\\\' % u' & '.join(first_row))
  output_rows.extend(u'\\hline' for _ in xrange(2))
  output_rows.extend(u'%s \\\\' % u' & '.join(r) for r, _ in double_iter)

  last_row = rows[-1]

  output_rows.extend(u'\\hline' for _ in xrange(2))
  output_rows.append(u'%s \\\\' % u' & '.join(last_row))

  output_rows.append(u'\end{tabular}')


  return u'\n'.join(output_rows)

def render_syllable(tl):
  return u'\\textipa{%s}' %  u''.join(l.to_tipa() for l in tl)

def syllable_counts_to_table(syllable_counter):

  rows = [
    ['Counts'] +
    list(render_syllable(v) for v in syllable_counter.iter_vowells()) +
    ['Total'],
  ]
  for c in syllable_counter.iter_consonants():
    row = [render_syllable(c)]
    for v in syllable_counter.iter_vowells():
      syllable = c + v
      counts = syllable_counter.syllable_count(syllable)
      row.append(unicode(counts))
    row.append(unicode(syllable_counter.syllable_with_consonant_count(c)))
    rows.append(row)
  rows.append(['Total'] + 
    list(
      unicode(syllable_counter.syllable_with_vowell_count(v))
      for v in syllable_counter.iter_vowells()
    ) + [
      unicode(syllable_counter.total_count())
    ]
  )
  return rows

def syllable_observed_expected_to_table(syllable_counter):

  f = u'%.3f'
  rows = [
    ['O/E'] +
    list(render_syllable(v) for v in syllable_counter.iter_vowells()) +
    ['Total'],
  ]
  total_count_float = syllable_counter.total_count()
  for c in syllable_counter.iter_consonants():
    row = [render_syllable(c)]
    consonant_count_float = float(
        syllable_counter.syllable_with_consonant_count(c))
    for v in syllable_counter.iter_vowells():
      syllable = c + v
      counts = float(syllable_counter.syllable_count(syllable))
      expected = (consonant_count_float *
                  float(syllable_counter.syllable_with_vowell_count(v)))
      row.append(f % (counts*total_count_float/expected))
    row.append(f % (consonant_count_float/total_count_float))
    rows.append(row)
  rows.append(['Total'] + 
    list(
      f % (float(syllable_counter.syllable_with_vowell_count(v))/
           total_count_float)
      for v in syllable_counter.iter_vowells()
    ) + [
      f % (1)
    ]
  )
  return rows


def dump_to_file(filename, data):
  with open(filename, "w") as f:
    f.write(data)


def process_data(vowells, consonant_clusters, syllable_counts, outdir):
  vowells = list(v for v in vowells if not any(vl.is_nasal for vl in v))
  all_data = SyllableCounter(syllable_counts, vowells, consonant_clusters)
  _MIN_SIGNIFICANT_COUNT = 10

  common_vowells = {
      v for v in all_data.iter_vowells()
      if all_data.syllable_with_vowell_count(v) >= _MIN_SIGNIFICANT_COUNT}
  common_consonants = {
      c for c in all_data.iter_consonants()
      if all_data.syllable_with_consonant_count(c) >= _MIN_SIGNIFICANT_COUNT}

  common_data = SyllableCounter(
      syllable_counts,
      common_vowells,
      common_consonants,
  )

  dump_to_file(
      os.path.join(outdir, 'syllable_counts.tex'),
      make_tabular(syllable_counts_to_table(common_data)).encode('utf-8')
  )
  dump_to_file(
      os.path.join(outdir, 'syllable_ratios.tex'),
      make_tabular(syllable_observed_expected_to_table(common_data)).encode('utf-8')
  )
  return 


def compute_counts(word_counts, outdir):
  syllable_counts = defaultdict(lambda: 0)
  cluster_counts = defaultdict(lambda: 0)
  for word in word_counts.keys():
    for s in word.iter_syllables():
      syllable_counts[s.letters()] += 1
      for cl in iter_clusters(s.iter_letters()):
        cluster_counts[cl] += 1

  vowell_set = set()
  consonant_cluster_set = set([tuple()])
  for k in cluster_counts.keys():
    if len(k) == 1 and k[0].is_vowell():
      vowell_set.add(k)
    else:
      consonant_cluster_set.add(k)

  process_data(vowell_set, consonant_cluster_set, syllable_counts, outdir)


def analyze(filename, outdir):
  if not os.path.isdir(outdir):
    os.mkdir(outdir)
  word_counts = load_word_counts(filename)
  print "Loaded %d words" % len(word_counts)

  compute_counts(word_counts, outdir)


if __name__ == "__main__":
  def raiseUsage(arg):
    raise SystemExit(
        'Invalid invocation(%s)!\n\nUsage: python %s <csv-file-to-analyze>' %
        (arg, sys.argv[0]))

  if len(sys.argv) != 2:
    raiseUsage('requires an argument')

  filename = sys.argv[1]
  if not os.path.isfile(filename):
    raiseUsage('%s not a file' % repr(filename))
  analyze(filename, './out')
