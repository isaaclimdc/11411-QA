#!/usr/local/bin/python

import argparse, logging, os, sys, string, re, subprocess, ntpath
from qranker import rank
from generic import makeGenericQuestions
from specific import makeSpecificQuestions
from util import extractEntity

parser = argparse.ArgumentParser(description="Ask")
parser.add_argument("--txt", help="Original txt file", required="True")
parser.add_argument("--tagged", help="Corresponding tagged file. Adding this \
    will drastically reduce runtime. Otherwise a tagged file is generated \
    from the txt file.")
args = parser.parse_args()

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
print "~ DONE!\n"

#######################
###### Constants ######
#######################

PERSON_TAG = "/PERSON"
ORGANIZATION_TAG = "/ORGANIZATION"
LOCATION_TAG = "/LOCATION"
DATE_TAG = "/DATE"
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
  appendages = [',', "'s", ".''", "'ve", "n't", "'", "''"]
  for appendage in appendages:
    if word == appendage:
      return True
  return False

def condenseWords(question_parts):
  i = 0
  while i < len(question_parts):
    if i != 0 and appendToPreviousWord(question_parts[i]):
      word = question_parts[i]
      question_parts[i-1] = question_parts[i-1] + word
      question_parts = question_parts[:i] + question_parts[i+1:]
    else:
      if question_parts[i] == "``":
        question_parts[i] = question_parts[i] + question_parts[i+1]
        question_parts = question_parts[:i+1] + question_parts[i+2:]
      i+=1
  return question_parts

def removePunctuation(question_parts):
  punctuation = ['.', ',', '?']
  for p in punctuation:
    if question_parts[-1] == p:
      question_parts = question_parts[:-1]
  return question_parts

def appendQuestionMark(question_parts):
  last_word = question_parts[-1]
  question_parts[-1] = last_word + '?'
  return question_parts

def appendQuotes(question_parts):
  question_parts[1] = removeTag(question_parts[0]) + question_parts[1]
  question_parts[-2] = removeTag(question_parts[-2]) + question_parts[-1]
  question_parts = question_parts[1 : -1]
  return question_parts

# Truncate sentence after first occurence of "," or ";".
# This is usually enough for a question.
def truncateSentence(words):
  for i in xrange(0, len(words)):
    firstChar = words[i][0]
    if firstChar == ',' or firstChar == ';':
      return words[:i]

  return words

# Takes into account situations like
# 'He was about to do this when person, sent by blah, arrived'
def truncateSentence2(words):
  subsentence_index = -1
  for i in xrange(len(words)):
    first_char = words[i][0]
    if first_char == ';':
      return words[:i]
    elif first_char == ',' and subsentence_index != -1:
      words = words[:subsentence_index] + words[i + 1:]
      return words
    elif first_char == ',':
      subsentence_index = i
  return words

def hasRootWord(word, root_word):
  slash_index = word.find('/')
  start_index = slash_index + 1
  end_index = word.find('/', start_index)

  actual_root_word = word[start_index : end_index]
  return actual_root_word == root_word

# See if the given root words are the root
# of any of the given words
def containsKeyRootWords(words, root_words):
  for word in words:
    for root_word in root_words:
      if hasRootWord(word, root_word):
        return True
  return False

def fixTense(word):
  slash_index = word.find('/')
  start_index = slash_index + 1
  end_index = word.find('/', start_index)

  correct_tense = word[start_index : end_index]
  word = correct_tense + word[slash_index :]
  return word

def removeTagsFromWords(question_parts):
 for i in range(len(question_parts)):
    question_parts[i] = removeTag(question_parts[i])
 return question_parts  

def putInQuestionFormat(question_parts):
  question_parts = removeTagsFromWords(question_parts)
  question_parts = condenseWords(question_parts)
  question_parts = removePunctuation(question_parts)
  question_parts = appendQuestionMark(question_parts)
  question = " ".join(question_parts)
  question = cleanQuestion(question)
  return question


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
    #if (hasTag(words[j], VERB_TAG_1) or hasTag(words[j], VERB_TAG_2)) and not found_verb:
      #words[j] = fixTense(words[j])
      #found_verb = True
    #word = removeTag(words[j])
    #if appendToPreviousWord(word):
     # prev_word = question_parts[len(question_parts)-1]
     # question_parts[len(question_parts)-1] = prev_word + word
    #else:
    question_parts.append(words[j])
  
  if containsKeyRootWords(words, ['star']):
    question_parts[0] = "What"
  #question_parts = question_parts + words
  question = putInQuestionFormat(question_parts)
  return question

# Find sentences that we can turn into
# simple 'who' questions.
def makeWhoQuestions(sentences):
  who_questions = []
  for sentence in sentences:
    sentence = sentence.strip()
    words = sentence.split()

    words = truncateSentence2(words)

    # Reject questions shorter than length 5
    if len(words) >= 5:
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
  question_parts = ['[WHERE]', 'Where', 'did']
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

  question = putInQuestionFormat(question_parts)
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
  if len(parts) == 0:
      return parts
      
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
  question_parts = ["[WHEN]", "When", "did"] + question_parts
  question = putInQuestionFormat(question_parts)

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
      # if hasTag(word, DATE_TAG):
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

##########################################
######### Quote Questions ################
##########################################

def findQuoteQuestions(tagged_sentences):
  quote_questions = []
  root_words = ['say', 'comment']
  for sentence in tagged_sentences:
    found_quote = False
    start_index = -1
    sentence = sentence.strip()
    words = sentence.split()
    for i in range(len(words)):
      if hasTag(words[i], "/``"):
        found_quote = True
        start_index = i
      elif found_quote and hasTag(words[i], "/''"):
#        print "words", words
        # Entire sentence is a quote, so chances are 
        # someone said it. We also want to remove edge cases like
        # Clint 'Drew' Dempsey so length must be greater than 4.
        if ((start_index == 0 and (i == (len(words) - 1))) or
           ((i - start_index > 4) and containsKeyRootWords(words, root_words))):
          # There are some quotes we don't want such as
          # what someone's shirt said.
          question_parts = words[start_index + 1 : i] 
          question_parts = removeTagsFromWords(question_parts)
          question_parts = removePunctuation(question_parts)
          question_parts = [words[start_index]] + question_parts + [words[i]]
          question_parts = appendQuotes(question_parts)
          question_parts = ['[QUOTE]', 'Who', 'said'] + question_parts
          question = putInQuestionFormat(question_parts)       
          quote_questions.append(question)
          print question
        found_quote = False
  return quote_questions

########################
###### Procedural ######
########################

def tagData(file_path):
  # To use preprocessed tag file, just give ask a .tag file:
  #     ./ask.py tagged/clint_dempsey_ans.tag
  # To tag then process (slow!), just give ask a .txt file:
  #     ./ask.py ../test_data/clint_dempsey_ans.txt

  if file_path[-4:] == ".tag":
    # Preprocessed tag file
    tagged_file_path = file_path
  else:
    # Process the tagged data
    if not os.path.exists('tagged'):
      os.makedirs('tagged')
    print file_path
    # Raw text file. Must tag it first (slow!)
    subprocess.check_call(['./tag_data.sh', file_path, \
      "../ask/tagged/", "lemma NER POS"])
    tagged_file_name = ntpath.basename(file_path)
    tagged_file_path = "tagged/" + tagged_file_name[:-4] + ".tag"

  tagged_file = open(tagged_file_path, 'r')
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

def generateQuestions(tagged_sentences, original_file):
  questions = []
  questions += makeWhoQuestions(tagged_sentences)
  questions += makeWhenQuestions(tagged_sentences)
  questions += makeWhereQuestions(tagged_sentences)
  questions += findQuoteQuestions(tagged_sentences)
  with open(original_file) as f:
    content = f.read()
    generic_questions = makeGenericQuestions(content, tagged_sentences)
    if generic_questions:
      questions += generic_questions
    specific_questions = makeSpecificQuestions(content, tagged_sentences)
    questions += specific_questions

  return questions

def rankQuestions(questions, file_path):
  ranked_questions = rank(questions)
  # Write ranked questions to a file.
  if not os.path.exists('rank'):
    os.makedirs('rank')
  rank_file = open('rank/rank_' + ntpath.basename(file_path), 'w')
  for ranked_question in ranked_questions:
    rank_file.write(str(ranked_question[1]) + ' ' + ranked_question[0] +'\n')
  rank_file.close()

  return ranked_questions

# Write questions to file.
def writeQuestions(questions, file_path):
  if not os.path.exists('questions'):
    os.makedirs('questions')
  file_name = ntpath.basename(file_path)[:-3] + "txt"
  question_file = open('questions/questions_' + file_name, 'w')
  for question in questions:
    question_file.write(question+'\n')
  question_file.close()

# TODO(mburman): use the logging module instead of prints
# TODO(mburman): let user specify logging level
if __name__ == '__main__':
  file_path = args.txt
  
  original_file = '../test_data/' + file_path
  if args.tagged:
    file_path = args.tagged

  print "~ Tagging data..."
  tagged_sentences = tagData(file_path)
  print "~ DONE!\n"

  print "~ Generating Questions..."
  questions = generateQuestions(tagged_sentences, original_file)
  print "~ DONE!\n"

  print "~ Ranking questions..."
  ranked_questions = rankQuestions(questions, file_path)
  print "~ DONE!\n"

  print "~ Writing questions to file..."
  writeQuestions(questions, file_path)
  print "~ DONE!\n"

  #END






# TODO(sjoyner): Problems to handle:
# In the Dempsay article there is a typo. It says Dempsay 3rd goal was scored...
# so our question generator makes the sentence Who 3rd goal was scored
# The name entity recognizer marks commas and similar things as separate words
# so we need to fix that when we recombine sentences
# Need to deal with sentences like Bob was born here and he did this. He
# should be converted.
