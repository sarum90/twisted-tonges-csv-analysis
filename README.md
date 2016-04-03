# twisted-tonges-csv-analysis

[![Build Status](https://travis-ci.org/sarum90/twisted-tonges-csv-analysis.svg?branch=master)](https://travis-ci.org/sarum90/twisted-tonges-csv-analysis)

Analysis for csvs exported from the twisted tongues language documentation website.

# To run

Download a CSV of all of the word dictionary analysis on it run the following:

```bash
python ./analyse.py <path-to-word-dictionary.csv> <path-to-output-directory>
```

# Development

It might be convenient to make a `local.mak` file inside your project to run
the script with common arguments for your computer.

For instance, on my development setup I've downloaded a word dictionary, and I
like to run the unit tests for this package as well as running the script
outputting tables to a "./out" directory.

Thus, my `local.mak` file looks like the following:


```Makefile
default: test my_test

my_test:
	python analyse.py "$(HOME)/Downloads/word_dictionary.csv" ./out
```
