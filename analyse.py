#!/usr/bin/env python

import sys
import os
from itertools import izip
from collections import defaultdict
from csv_loader import csv_rows
from word_parsing import (make_word, WordParseError)

def analyze(filename):
  raw_rows = csv_rows(filename)
  word_counts = defaultdict(lambda: 0)

  for line_number, raw_row in enumerate(raw_rows, 2):
    count = int(raw_row["count"])
    ipa = raw_row["IPA"]

    # Work around a passage with an error in it:
    gloss = raw_row["Gloss"] or raw_row["Text"]

    category = raw_row["Category"]

    skipword_characters = {'?'}
    try:
      for i, g in izip(ipa.split('/'), gloss.split('/')):
        word = make_word(i, g, category)
        word_counts[word] += count
    except WordParseError as e:
      print u"Error on line %d: %s" % (line_number, repr(e))
    except IndexError as e:
      unknown_index = e.args[0]
      if unknown_index in skipword_characters:
        print u"Bad char on line %d: %s" % (line_number, repr(e))
      else:
        print "FATAL ERROR ON LINE %d" % line_number
        raise
    except:
      print "FATAL ERROR ON LINE %d" % line_number
      raise

  print "Loaded %d words" % len(word_counts)



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
  analyze(filename)
