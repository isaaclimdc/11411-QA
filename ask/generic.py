#!/usr/local/bin/python
from util import extractEntity

# Generic questions for each type of file we get.
generic_soccer = [
    'When was [ENTITY] born?',
    'Where was [ENTITY] born?',
    'Where did [ENTITY] grow up?',
    'What are some notable awards [ENTITY] has won?'
]

generic_constellation = [
    'Where is [ENTITY] located?',
    'Is [ENTITY] in the zodiac?'
    'Is [ENTITY] one of the 88 modern constellations?',
    'Is Ptolemy credited with describing [ENTITY]?'
]

generic_movie = [
    'Who directed [ENTITY]?',
    'Is [ENTITY] a British film?',
    'Who wrote [ENTITY]?',
    'When was [ENTITY] released?'
]

generic_language = [
    'Is [ENTITY] a west germanic language?',
    'Is [ENTITY] a programming language?',
    'Is [ENTITY] a romance language?',
    'How did [ENTITY] originate?'
]

def makeGenericQuestions(content, tagged_sentences):
  # Analyze the file to figure out which type it is - movie, soccer players,
  # constellations etc and add generic questions based on that.
  to_return = []
  entity = extractEntity(content)
  if not entity:
    return to_return

  print "~ Entity: " + entity
  if isSoccer(content):
    for question in generic_soccer:
      question = question.replace('[ENTITY]', entity)
      to_return.append('[GENERIC]' + question)
    return to_return

  if isConstellation(content):
    for question in generic_constellation:
      question = question.replace('[ENTITY]', entity)
      to_return.append('[GENERIC]' + question)
    return to_return

  if isLanguage(content):
    for question in generic_language:
      question = question.replace('[ENTITY]', entity)
      to_return.append('[GENERIC]' + question)
    return to_return

  if isMovie(content):
    for question in generic_movie:
      question = question.replace('[ENTITY]', entity)
      to_return.append('[GENERIC]' + question)
    return to_return

# TODO(mburman): These checks need to be stronger.
def isSoccer(content):
  if 'soccer' in content:
    return True

def isConstellation(content):
  if 'constellation' in content:
    return True

def isLanguage(content):
  if 'language' in content:
    return True

def isMovie(content):
  if 'directed' in content:
    return True
