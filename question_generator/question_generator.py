#!/usr/local/bin/python

import logging, sys, string, re
lib_path = os.path.abspath('../helpers')
sys.path.append(lib_path)
from nltk_helper import splitIntoSentences2, getSynonyms

# TODO(mburman): use the logging module instead of prints
# TODO(mburman): let user specify logging level
if __name__ == '__main__':
  if len(sys.argv) < 2:
    print 'Usage: ' + \
        'python question_generator.py <file>\n'
    sys.exit(0)

    # TODO: implement a question generator
