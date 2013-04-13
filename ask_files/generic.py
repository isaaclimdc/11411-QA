#!/usr/local/bin/python

# Certain generic questions can be asked irrespective of the actual entity
# being talked about based on the category it falls in. For example, wrt movies,
# 'Who directed (...)?' is a valid question.

from util import *

# Generic questions for each type of file we get.
generic_soccer = [
    'When was [ENTITY] born?',
    'Where was [ENTITY] born?',
    'Where did [ENTITY] grow up?',
    'What are some notable awards [ENTITY] has won?'
]

generic_constellation = [
    'Where is [ENTITY] located?',
    'Is [ENTITY] in the zodiac?',
    'Is [ENTITY] one of the 88 modern constellations?',
    'Is Ptolemy credited with describing [ENTITY]?'
]

generic_movie = [
    'Who directed [ENTITY]?',
    'Is [ENTITY] a British film?',
    'Who wrote [ENTITY]?',
    'When was [ENTITY] released?',
    'How many academic awards did [ENTITY] win?'
]

generic_language = [
    'Is [ENTITY] a West Germanic language?',
    'Is [ENTITY] a programming language?',
    'Is [ENTITY] a romance language?',
    'How did [ENTITY] originate?'
]

generic_programming_language = [
    'Who created [ENTITY]?',
    'When was [ENTITY] created?',
    'Why was [ENTITY] created?',
    'Is [ENTITY] an object oriented language?'
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

  if isProgrammingLanguage(content):
    for question in generic_programming_language:
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


