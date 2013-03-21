#!/usr/local/bin/python

import logging, os, sys, string, re, subprocess, ntpath
from qranker import rank

# Check dependencies
def checkDependencies():
  if os.path.isdir("../libraries/en") and \
     os.path.isdir("../libraries/stanford-corenlp"):
    return
  else:
    print "Dependencies not installed.\nRun cd.. then ./build_dependencies.sh"
    sys.exit(0)

if len(sys.argv) < 2:
  print 'Usage: ./ask.py <article_file>\n'
  sys.exit(0)

print "~ Importing required libraries..."
checkDependencies()
lib_path = os.path.abspath('../libraries')
sys.path.append(lib_path)

from nltk_helper import splitIntoSentences2, getSynonyms
import en
print "DONE!\n"


#######################
###### Constants ######
#######################

PERSON_TAG = "/PERSON"
ORGANIZATION_TAG = "/ORGANIZATION"
LOCATION_TAG = "/LOCATION"
VERB_TAG_1 = "/VBD"
VERB_TAG_2 = "/VBG"



##############################
###### Helper functions ######
##############################

# Check to see if a word has a given tag
# (i.e person, place)
def hasTag(word, tag):
  return (tag in word)

def removeTag(word):
  tag_index = word.find('/')
  if tag_index != -1:
    word = word[:tag_index]
  return word

def appendToPreviousWord(word):
  appendages = [',', "'s"]
  for appendage in appendages:
    if word == appendage:
      return True
  return False

def removePeriods(question_parts):
  # If last token of the sentence is a period, remove it.
  if question_parts[-1] == ".":
    question_parts = question_parts[:-1]
  return question_parts

def appendQuestionMark(question_parts):
  last_word = question_parts[-1]
  question_parts[-1] = last_word + '?'
  return question_parts 

# Truncate sentence after first occurence of "," or ";".
# This is usually enough for a question.  
def truncateSentence(words):
  end = len(words)
  for i in xrange(0, len(words)):
    firstChar = words[i][0]
    if firstChar == words[i][0]:
      end = i
      break
    words = words[:end]
  return words

def hasRootWord(word, root_word):
  slash_index = word.find('/')
  start_index = slash_index + 1
  end_index = word.find('/', start_index)

  actual_root_word = word[start_index : end_index]
  return actual_root_word == root_word

def fixTense(word):
  slash_index = word.find('/')
  start_index = slash_index + 1
  end_index = word.find('/', start_index)

  correct_tense = word[start_index : end_index]
  word = correct_tense + word[slash_index : ]
  return word



#############################
###### "Who" questions ######
#############################



def makeWhoQuestion(words, question_parts):
  i = 0
  # Ignore the name
  for i in xrange(0, len(words)):
    if not hasTag(words[i], PERSON_TAG):
      break
  found_verb = False
  for j in xrange(i, len(words)):
    if (hasTag(words[j], VERB_TAG_1) or hasTag(words[j], VERB_TAG_2)) and not found_verb:
      words[j] = fixTense(words[j])
      found_verb = True
    word = removeTag(words[j])
    if appendToPreviousWord(word):
      prev_word = question_parts[len(question_parts)-1]
      question_parts[len(question_parts)-1] = prev_word + word
    else:
      question_parts.append(word)
  
  question_parts = removePeriods(question_parts)
  question_parts = appendQuestionMark(question_parts)
  question = ' '.join(question_parts)
  return question

# Find sentences that we can turn into
# simple 'who' questions.
def makeWhoQuestions(sentences):
  who_questions = []
  for sentence in sentences:
    sentence = sentence.strip()
    words = sentence.split()

    words = truncateSentence(words)

    # Reject questions shorter than length 5
    if len(words) < 5:
      continue

    if hasTag(words[0], PERSON_TAG):
      question = makeWhoQuestion(words, ['Who'])
      question = cleanQuestion(question)
      who_questions.append(question)
    else:
      against_question = False
      comma_found = False
      for i in xrange(len(words)):
        if hasTag(words[i], '/IN') and hasTag(words[i], '/against'):
          against_question = True
        elif hasTag(words[i], '/,') and against_question:
          question_words = words[i + 1 : ]
          # TODO(sjoyner): We need to figure out what this word refers to as this is
          # what the question is about
          if hasTag(question_words[0], '/PRP'):
            question_words = question_words[1 : ]
          question = makeWhoQuestion(question_words, ['Against', 'who', 'did', 'THING'])
          question = cleanQuestion(question)
          print question
          print
          who_questions.append(question)
          break
  return who_questions



###############################
###### "Where" questions ######
###############################

def makeWhereDidQuestion(words, start_index, end_index):
  question_parts = ['Where', 'did']
  found_verb = False
  for i in xrange(start_index, end_index):
    if (hasTag(words[i], VERB_TAG_1) or hasTag(words[i], VERB_TAG_2)) and not found_verb:
      words[i] = fixTense(words[i])
      foundVerb = True
    word = removeTag(words[i])
    if appendToPreviousWord(word):
      prev_word = question_parts[-1]
      question_parts[-1] = prev_word + word
    else:
      question_parts.append(word)
  
  question_parts = removePeriods(question_parts)
  question_parts = appendQuestionMark(question_parts)
  question = ' '.join(question_parts)
  return question

def containsSpecialCase(words, key_phrase):
  key_phrase_index = 0
  found_index = -1
  for i in xrange(len(words)):
    if hasRootWord(words[i], key_phrase[key_phrase_index]):
      if key_phrase_index == 0:
        found_index = i
      key_phrase_index += 1
    else:
      if (key_phrase_index > 0) and (not key_phrase_index == len(key_phrase)):
        found_index = -1
  return found_index

def makeWhereQuestions(sentences):
  where_questions = []
  for sentence in sentences:
    sentence = sentence.strip()
    words = sentence.split()

    words = truncateSentence(words)
    index = -1
    # Some where questions have the format
    # In LOCATION, this event occurred
    if len(words) > 0 and hasTag(words[0], 'In') and hasTag(words[0], '/IN'):
      foundLocation = False
      foundComma = False
      for i in xrange(len(words)):
        if hasTag(words[i], LOCATION_TAG) or hasTag(words[i], ORGANIZATION_TAG):
          foundLocation = True
        # Found a potential question
        elif hasTag(words[i], ','):
          if foundLocation:
            foundComma = True
        elif hasTag(words[i], PERSON_TAG) or hasTag(words[i], ORGANIZATION_TAG):
          if foundComma:
            index = i
            break
    if index != -1:
      question = makeWhereDidQuestion(words, index, len(words))
      question = cleanQuestion(question)
      where_questions.append(question)
    # Special case time!
#    else:
 #     index = containsSpecialCase(words, ['grow', 'up'])
  #    if index != -1:
   #     question = makeWhereDidQuestion
  return where_questions



##############################
###### "When" questions ######
##############################

# Remove extra words/symbols, RECURSIVELY :(
def recClean(parts):
  firstWord = parts[0]
  lastWord = parts[-1]
  if firstWord == "on" or firstWord == "." or \
     firstWord == "," or firstWord.isdigit():
    return recClean(parts[1:])
  if lastWord == "on" or lastWord == "." or \
     lastWord == "," or lastWord.isdigit():
    return recClean(parts[:-1])

  return parts

# Does the dirty work to transform a raw sentence containing
# a date reference to a "when" question.
def processWhenQuestion(question_parts):
  question_parts = recClean(question_parts)

  # Convert the subject verb to present tense using NodeBox
  # TODO(idl):A smarter version of this. This only takes
  # care of 1 case.
  try:
    question_parts[1] = en.verb.present(question_parts[1])
  except:
    pass

  question_parts = truncateSentence(question_parts)

  # Join everything together.
  question_parts = ["When", "did"] + question_parts
  question_parts = appendQuestionMark(question_parts)
  question = " ".join(question_parts)
  question = cleanQuestion(question)

  return question

# Find sentences that we can turn into
# simple 'when' questions.
def makeWhenQuestions(sentences):
  # Pick out occurences of dates in the text
  r = re.compile('january|february|march|april|may|june|july|august|september|october|november|December.*', re.IGNORECASE)

  when_questions = []
  for sentence in sentences:
    sentence = sentence.strip()
    words = sentence.split()
    n = len(words)

    # Strip NER tags; don't need them for when questions
    for i in xrange(0, n):
      words[i] = removeTag(words[i])

    # Pick out the date occurences
    for i in xrange(0, n):
      word = words[i]
      if r.match(word):
        if i > n/2:
          # Extract first half of sentence
          extracted = words[:i]
        else:
          # Extract second half of sentence
          extracted = words[i+1:]

        question = processWhenQuestion(extracted)
        when_questions.append(question)

  return when_questions



########################
###### Procedural ######
########################

def tagData(file_name):
  file_path = file_name
  tagged_file = open(file_name, 'r')
  file_path = '../../question_generator' + file_name
  #subprocess.call(['./parse_text.sh', file_path])
  #print "Tagging data..."

  # Tag data.
  if not os.path.exists('tagged'):
    os.makedirs('tagged')
  tagged_file = open('tagged/tagged_' + ntpath.basename(file_name), 'w+')

  # Executes Stanford NER.
  subprocess.call(['java', '-cp', '../libraries/stanford-ner/stanford-ner.jar', '-mx600m',
                  'edu.stanford.nlp.ie.crf.CRFClassifier', '-loadClassifier',
                  '../libraries/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz', '-textFile', file_path], stdout=tagged_file)

  tagged_file.seek(0)
  sentences = tagged_file.readlines()
  tagged_file.close()

  return sentences

# Final pass over a question to remove unnecessary tags.
def cleanQuestion(question):
  # TODO(mburman): a single pass replace might be more efficient.
  question = question.replace('-LRB- ', '(')
  question = question.replace(' -RRB-', ')')
  question = question.replace('--', '-')

  return question

def generateQuestions(sentences):
  questions = []
  questions += makeWhoQuestions(sentences)
  questions += makeWhenQuestions(sentences)
  questions += makeWhereQuestions(sentences)

  return questions

def rankQuestions(questions, file_name):
  ranked_questions = rank(questions)
  # Write ranked questions to a file.
  if not os.path.exists('rank'):
    os.makedirs('rank')
  rank_file = open('rank/rank_' + ntpath.basename(file_name), 'w')
  for ranked_question in ranked_questions:
    rank_file.write(str(ranked_question[1]) + ' ' + ranked_question[0] +'\n')
  rank_file.close()

  return ranked_questions

# Write questions to file.
def writeQuestions():
  if not os.path.exists('questions'):
    os.makedirs('questions')
  question_file = open('questions/questions_' + ntpath.basename(file_name), 'w')
  for question in questions:
    question_file.write(question+'\n')
  question_file.close()

# TODO(mburman): use the logging module instead of prints
# TODO(mburman): let user specify logging level
if __name__ == '__main__':
  file_name = sys.argv[1]

  print "~ Tagging data..."
  sentences = tagData(file_name)
  print "DONE!\n"

  print "~ Generating Questions..."
  questions = generateQuestions(sentences)
  print "DONE!\n"

  print "~ Ranking questions..."
  ranked_questions = rankQuestions(questions, file_name)
  print "DONE!\n"

  print "~ Writing questions to file..."
  writeQuestions()
  print "DONE!\n"

  #END






# TODO(sjoyner): Problems to handle:
# In the Dempsay article there is a typo. It says Dempsay 3rd goal was scored...
# so our question generator makes the sentence Who 3rd goal was scored
# The name entity recognizer marks commas and similar things as separate words
# so we need to fix that when we recombine sentences
# Need to deal with sentences like Bob was born here and he did this. He
# should be converted.