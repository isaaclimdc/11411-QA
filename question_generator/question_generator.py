#!/usr/local/bin/python

import logging, os, sys, string, re, subprocess
lib_path = os.path.abspath('../helpers')
sys.path.append(lib_path)
from nltk_helper import splitIntoSentences2, getSynonyms

PERSON_TAG = "/PERSON"


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
  while hasNameEntityTag(words[i], PERSON_TAG):
    i+=1
  for j in range(i,len(words)):
    word = removeTag(words[j])
    if appendToPreviousWord(word):
      prev_word = question_parts[len(question_parts)-1]
      question_parts[len(question_parts)-1] = prev_word + word
    else:
      question_parts.append(word)
  # Last part of sentence is ending punctuation like a period.
  question_parts = question_parts[:len(question_parts)-1]
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
    if hasNameEntityTag(words[0], PERSON_TAG):
      question = makeWhoQuestion(words)
      who_questions.append(question)
  return who_questions

# Check dependencies
def check_dependencies():
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
  
  file_name = sys.argv[1]

  file_path = '../question_generator/' + file_name

  check_dependencies()
  
  tagged_file = open('tagged_' + file_name, 'w+')
  # Executes Stanford name entity recognizer
  subprocess.call(['java', '-cp', '../stanford-ner-2012-11-11/stanford-ner.jar', '-mx600m',
                  'edu.stanford.nlp.ie.crf.CRFClassifier', '-loadClassifier',
                  '../stanford-ner-2012-11-11/classifiers/english.all.3class.distsim.crf.ser.gz', '-textFile', file_path], stdout=tagged_file)
 
  tagged_file.seek(0)
  sentences = tagged_file.readlines()
  tagged_file.close()
  

  file_name = sys.argv[1]
  file_path = '../question_generator/' + file_name

  tagged_file = open('tagged_' + file_name, 'w+')
  # Executes Stanford name entity recognizer
  subprocess.call(['java', '-cp', '../stanford-ner-2012-11-11/stanford-ner.jar', '-mx600m',
                  'edu.stanford.nlp.ie.crf.CRFClassifier', '-loadClassifier',
                  '../stanford-ner-2012-11-11/classifiers/english.all.3class.distsim.crf.ser.gz', '-textFile', file_path], stdout=tagged_file)

  tagged_file.seek(0)
  sentences = tagged_file.readlines()
  tagged_file.close()

>>>>>>> b8a8e824dfc6f124fc322ce01735961137f981fe
  questions = makeWhoQuestions(sentences)
  # Write questions to a file
  question_file = open('questions_' + file_name, 'w')
  for question in questions:
    question_file.write(question+'\n')
  question_file.close()
#TODO(sjoyner): Problems to handle:
# 's at end of name entity is counted as separate word
# In the Dempsay article there is a typo. It says Dempsay 3rd goal was scored...
# so our question generator makes the sentence Who 3rd goal was scored
<<<<<<< HEAD
# The name entity recognizer marks commas and similar things as separate words 
=======
# The name entity recognizer marks commas and similar things as separate words
>>>>>>> b8a8e824dfc6f124fc322ce01735961137f981fe
# so we need to fix that when we recombine sentences
# Need to deal with sentences like Bob was born here and he did this. He should be converted.
