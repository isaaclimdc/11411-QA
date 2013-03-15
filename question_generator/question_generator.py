#!/usr/local/bin/python

import logging, os, sys, string, re, subprocess, ntpath
lib_path = os.path.abspath('../helpers')
sys.path.append(lib_path)
from nltk_helper import splitIntoSentences2, getSynonyms

PERSON_TAG = "/PERSON"
LOCATION_TAG = "/LOCATION"
# Check to see if a word has a given tag
# (i.e person, place)
# TODO(sjoyner): We'll probably be able to use this function
# for other things beside name entity tagging.
def hasNameEntityTag(word, tag):
  return word.endswith(tag)

def removeTag(word):
  tag_index = word.rfind('/')
  if tag_index != -1:
    word = word[:tag_index]
  return word

def appendToPreviousWord(word):
  appendages = [',', "'s"]
  for appendage in appendages:
    if word == appendage:
      return True
  return False

def makeWhoQuestion(words):
  question_parts = ['Who']
  i = 0
  # Ignore the name
  for i in xrange(0, len(words)):
    if not hasNameEntityTag(words[i], PERSON_TAG):
      break

  for j in xrange(i, len(words)):
    word = removeTag(words[j])
    if appendToPreviousWord(word):
      prev_word = question_parts[len(question_parts)-1]
      question_parts[len(question_parts)-1] = prev_word + word
    else:
      question_parts.append(word)

  # If last token of the sentence is a period, remove it.
  if question_parts[-1] == ".":
    question_parts = question_parts[:-1]

  last_word = question_parts[len(question_parts)-1]
  question_parts[len(question_parts)-1] = last_word + '?'
  question = ' '.join(question_parts)
  return question

# Find sentences that we can turn into
# simple 'who' questions.
def makeWhoQuestions(sentences):
  who_questions = []
  for sentence in sentences:
    sentence = sentence.strip()
    words = sentence.split()

    # Truncate sentence after first occurence of "," or ";".
    # This is usually enough for a question.
    end = len(words)
    for i in xrange(0, len(words)):
      firstChar = words[i][0]
      if firstChar == ',' or firstChar == ";":
        end = i
        break
    words = words[:end]

    # Reject questions shorter than length 5
    if len(words) < 5:
      continue

    if hasNameEntityTag(words[0], PERSON_TAG):
      question = makeWhoQuestion(words)
      question = cleanQuestion(question)
      who_questions.append(question)

  return who_questions

# Final pass over a question to remove unnecessary tags.
def cleanQuestion(question):
  # TODO(mburman): a single pass replace might be more efficient.
  question = question.replace('-LRB- ', '(')
  question = question.replace(' -RRB-', ')')
  question = question.replace('--', '-')
  return question

# Check dependencies
def checkDependencies():
  if os.path.isdir("../stanford-ner-2012-11-11"):
    return
  else:
    print "Dependencies not installed.\nRun ./build_dependencies.sh"
    sys.exit(0)

# TODO(mburman): use the logging module instead of prints
# TODO(mburman): let user specify logging level
if __name__ == '__main__':
  if len(sys.argv) < 2:
    print 'Usage: ' + \
        'python question_generator.py <file>\n'
    sys.exit(0)

  checkDependencies()
  file_name = sys.argv[1]
  file_path = '../question_generator/' + file_name

  # Tag data.
  if not os.path.exists('tagged'):
    os.makedirs('tagged')
  tagged_file = open('tagged/tagged_' + ntpath.basename(file_name), 'w+')
  # Executes Stanford name entity recognizer.
  subprocess.call(['java', '-cp', '../stanford-ner-2012-11-11/stanford-ner.jar', '-mx600m',
                  'edu.stanford.nlp.ie.crf.CRFClassifier', '-loadClassifier',
                  '../stanford-ner-2012-11-11/classifiers/english.all.3class.distsim.crf.ser.gz', '-textFile', file_path], stdout=tagged_file)
  tagged_file.seek(0)
  sentences = tagged_file.readlines()
  tagged_file.close()

  file_name = sys.argv[1]
  file_path = '../question_generator/' + file_name

  questions = makeWhoQuestions(sentences)

  # Write questions to a file.
  if not os.path.exists('questions'):
    os.makedirs('questions')
  question_file = open('questions/questions_' + ntpath.basename(file_name), 'w')
  for question in questions:
    question_file.write(question+'\n')
  question_file.close()

#TODO(sjoyner): Problems to handle:
# 's at end of name entity is counted as separate word
# In the Dempsay article there is a typo. It says Dempsay 3rd goal was scored...
# so our question generator makes the sentence Who 3rd goal was scored
# The name entity recognizer marks commas and similar things as separate words
# so we need to fix that when we recombine sentences
# Need to deal with sentences like Bob was born here and he did this. He should be converted.
