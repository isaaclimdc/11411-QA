#!/usr/local/bin/python

# Make specific questions by analyzing common patterns found in different
# categories. For example, for movies, generate questions for who portrayed a
# certain character.

from util import *
import os, sys

def generateSoccerQuestions(content, tagged_sentences):
  return []

def generateMovieQuestions(content, tagged_sentences):
  # Generate questions based on the cast members.
  to_return = []
  cast_begin = content.find("Cast\n")
  if cast_begin == -1:
    return to_return
  cast_end = cast_begin + content[cast_begin:].index("\n\n\n")
  if cast_end == -1:
    return to_return
  cast = content[cast_begin:cast_end]
  cast_lines = cast.split('\n')
  for item in cast_lines:
    if ' as ' in item:
      entity = item.split(' as ', 1)[0].strip()
      if len(entity.split()) <= 2:
        question = "[SPECIFIC] Who did " + entity + " play?"
        to_return.append(question)
  return to_return

def generateConstellationQuestions(content, tagged_sentences):
  to_return = []
  entity = extractEntity(content)
  if 'brightest' in content:
    to_return.append('[SPECIFIC] Name some of the brightest star(s) in ' + entity)
  return to_return

def generateLanguageQuestions(content, tagged_sentences):
  return []

def generateProgrammingLanguageQuestions(content, tagged_sentences):
  return []

def makeSpecificQuestions(content, tagged_sentences):
  questions = []

  if isSoccer(content):
    return generateSoccerQuestions(content, tagged_sentences)
  elif isMovie(content):
    return generateMovieQuestions(content, tagged_sentences)
  elif isConstellation(content):
    return generateConstellationQuestions(content, tagged_sentences)
  elif isLanguage(content):
    return generateLanguageQuestions(content, tagged_sentences)
  elif isProgrammingLanguage(content):
    return generateProgrammingLanguageQuestions(content, tagged_sentences)

  return questions
