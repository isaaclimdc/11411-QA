#!/usr/local/bin/python
import re

def extractEntity(content):
  entity = content.split('\n', 1)[0]
  replace_regex = re.compile('\.|\(programming\ language\)|language|\(film\)', re.IGNORECASE)
  entity = replace_regex.sub('', entity)
  return entity.strip()

# TODO(mburman): These checks need to be stronger.
def isSoccer(content):
  content = content.lower()
  if 'soccer' in content:
    return True

def isConstellation(content):
  if 'constellation' in content:
    return True

def isProgrammingLanguage(content):
  if 'programming language' in content:
    return True

def isLanguage(content):
  if 'language' in content:
    return True

def isMovie(content):
  movie_signals = ['directed', 'film']
  if all(x in content for x in movie_signals):
    extra_signals = ['star', 'played']
    if any(y in content for y in extra_signals):
      return True
