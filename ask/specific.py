#!/usr/local/bin/python

# Make specific questions by analyzing common patterns found in different
# categories. For example, for movies, generate questions for who portrayed a
# certain character.

from util import *

def generateSoccerQuestions(content, tagged_sentences):
  return []

def generateMovieQuestions(content, tagged_sentences):
  # Generate questions based on the cast members.
  to_return = []
  cast_begin = content.index("Cast\n")
  cast_end = cast_begin + content[cast_begin:].index("\n\n\n")
  cast = content[cast_begin:cast_end]
  cast_lines = cast.split('\n')
  for item in cast_lines:
    print item
    if ' as ' in item:
      entity = item.split(' as ', 1)[0].strip()
      print "entity " + entity
      question = "[SPECIFIC] Who did " + entity + " play?"
      to_return.append(question)
  return to_return

def generateConstellationQuestions(content, tagged_sentences):
  return []

def generateLanguageQuestions(content, tagged_sentences):
  return []

def generateProgrammingLanguageQuestions(content, tagged_sentences):
  return []

def makeSpecificQuestions(content, tagged_sentences):
  if isSoccer(content):
    return generateSoccerQuestions(content, tagged_sentences)
  if isMovie(content):
    return generateMovieQuestions(content, tagged_sentences)
  if isConstellation(content):
    return generateConstellationQuestions(content, tagged_sentences)
  if isLanguage(content):
    return generateLanguageQuestions(content, tagged_sentences)
  if isProgrammingLanguage(content):
    return generateProgrammingLanguageQuestions(content, tagged_sentences)
