#!/usr/local/bin/python
import re, sys

# Print only to stderr
def log(s):
  sys.stderr.write(s + "\n")

def extractEntity(content):
  entity = content.split('\n', 1)[0]
  replace_regex = re.compile('\.|\(programming\ language\)|language|\(film\)', re.IGNORECASE)
  entity = replace_regex.sub('', entity)
  return entity.strip()

# TODO(mburman): These checks need to be stronger.
def isSoccer(content):
  content = content.lower()
  soccer_signals = ['club', 'goals']
  if all(x in content for x in soccer_signals):
    extra_signals = ['competition', 'team', 'soccer', 'score']
    if any(y in content for y in extra_signals):
      return True

def isConstellation(content):
  content = content.lower()
  constellation_signals = ['constellation']
  if all(x in content for x in constellation_signals):
    extra_signals = ['Deep-sky', 'astronomy', 'visible']
    if any(y in content for y in extra_signals):
      return True

def isProgrammingLanguage(content):
  content = content.lower()
  programming_signals = ['programming language']
  if all(x in content for x in programming_signals):
    extra_signals = ['syntax', 'object-oriented', 'java']
    if any(y in content for y in extra_signals):
      return True

def isLanguage(content):
  content = content.lower()
  language_signals = ['language', 'vocabulary']
  if all(x in content for x in language_signals):
    extra_signals = ['linguistics', 'pronunciation', 'phonology']
    if any(y in content for y in extra_signals):
      return True

def isMovie(content):
  content = content.lower()
  movie_signals = ['directed', 'film']
  if all(x in content for x in movie_signals):
    extra_signals = ['star', 'played']
    if any(y in content for y in extra_signals):
      return True
