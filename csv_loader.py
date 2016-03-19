"""
Loads CSV data into dicts (1 dict per row) assuming the first row is the name
of the keys.
"""


import csv

def csv_rows(filename):
  """
  Generator that produces one dict for every row of a CSV file. Handles loading
  the file and 
  Loads filename `filename` and 

  :param unicode filename: The name of the file to 

  """
  with open(filename) as csvfile:
    reader = csv.DictReader(csvfile)
    line = 0
    try:
      for line, row in enumerate(reader, 2):
        # I should fix the website to not have these 3 random bytes at the
        # beginning. For now, just work around it.
        bv = row.pop('\xef\xbb\xbf"IPA"')
        row['IPA'] = bv
        yield {key: unicode(value, 'utf-8')
               for key, value in row.iteritems()}
    except Exception:
      print "Failure on line: ", line
      raise
