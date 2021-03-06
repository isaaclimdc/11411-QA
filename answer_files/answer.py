#!/afs/andrew.cmu.edu/usr/ysim/python-411/bin/python

import logging, os, sys, string, re
lib_path = os.path.abspath('../libraries')
sys.path.append(lib_path)
from nltk_helper import splitIntoSentences2, getSynonyms
from random import randint
from util import *

# Print only to stderr
def log(s):
  sys.stderr.write(s + "\n")

#######################
###### Constants ######
#######################

INSERTION_COST = 0
DELETION_COST = 1
REPLACEMENT_COST = 1
TRANSPOSITION_COST = 1

WORD_THRESHOLD = 2

# Synonym dict. Reset for every question.
glob_syn_dict = dict()
global_entity = ''

NO_VARS = ["No.", "Nope.", "That's a negative!"]
YES_VARS = ["Yes.", "Yup.", "Yes indeed!", "Definitely.", "Certainly.", "Sure."]

##############################
###### Helper functions ######
##############################

def splitSentence(sentence):
  s = sentence.split()
  for i in range(len(s)):
    s[i] = s[i].strip()
  return s

def genYesAns():
  r = randint(0, len(YES_VARS)-1)
  return YES_VARS[r]

def genNoAns():
  r = randint(0, len(NO_VARS)-1)
  return NO_VARS[r]

#################################
###### Levenshtein-Damerau ######
#################################

def levenshteinDistance(word1, word2, memo):
	len1 = len(word1)
	len2 = len(word2)

	if (word1 == ""): return len2
	if (word2 == ""): return len1

	key = str([word1, word2])
	if key in memo:
		return memo[key]

	word1MinusOne = word1[:(len1-1)]
	word2MinusOne = word2[:(len2-1)]
	if (word1[len1-1] == word2[len2-1]):
		count = levenshteinDistance(word1MinusOne, word2MinusOne, memo)
	else:
		count1 = levenshteinDistance(word1MinusOne,word2, memo) + 1
		count2 = levenshteinDistance(word1, word2MinusOne, memo) + 1
		count3 = levenshteinDistance(word1MinusOne, word2MinusOne, memo) + 1
		count = min(count1, count2, count3)
	memo[key] = count
	return count

def damerauDistance(s1, s2, memo):
  len1 = len(s1)
  len2 = len(s2)

  if (len1 == 0): return len2
  if (len2 == 0): return len1

  key = str([s1, s2])
  if key in memo:
    return memo[key]
  sentence1MinusOne = s1[:(len1-1)]
  sentence2MinusOne = s2[:(len2-1)]

  # TODO(mburman): Make the edit distance level depend on word size.
  # Instead of direct word comparison to see if two words are equal, say they're
  # equal if the levenshtein distance is less than some number. This helps us
  # identify similar words (eg 'contribute' and 'contributed' would now be the
  # same word)
  #distance_between_words = levenshteinDistance(s1[len1-1], s2[len2-1], dict())
  #if (distance_between_words <= WORD_THRESHOLD):
  # Actually, levenshtein like this becomes very expensive fast so stick with
  # direct string comparison for now
  if s1[len1-1] == s2[len2-1]:
    count = damerauDistance(sentence1MinusOne, sentence2MinusOne, memo)
  # Synonym matching
  elif s2[len2-1] in glob_syn_dict[s1[len1-1]]:
    count = damerauDistance(sentence1MinusOne, sentence2MinusOne, memo)
  else:
    count4 = float("infinity")
    if ((len1 > 1) and (len2 > 1)):
       lastWordSentence1 = s1[len1-1]
       secondLastWordSentence1 = s1[len1-2]
       lastWordSentence2 = s2[len2-1]
       secondLastWordSentence2 = s2[len2-2]

       # TODO(mburman): I don't think this if statement should be here.
       # Shouldn't you be able to interchange ANY two words in a sentence?
       #if ((lastWordSentence1 == secondLastWordSentence2) and
       #    (lastWordSentence2 == secondLastWordSentence1)):
       #count4 = damerauDistance(s1[:len1-2], s2[:len2-2], memo) + \
       #      TRANSPOSITION_COST

    # Numbers in a question are likely there for a reason. As a result, assign
    # high cost to deleting words which contain numbers.
    deleted_word = s1[len1-1];
    dynamic_deletion_cost = DELETION_COST
    dynamic_replacement_cost = REPLACEMENT_COST
    _digits = re.compile('\d')
    if _digits.search(deleted_word):
      dynamic_deletion_cost = 6
      dynamic_replacement_cost = 6

    count1 = damerauDistance(sentence1MinusOne,s2, memo) + dynamic_deletion_cost
    count2 = damerauDistance(s1, sentence2MinusOne, memo) + INSERTION_COST
    count3 = damerauDistance(sentence1MinusOne, sentence2MinusOne, memo) + \
        dynamic_replacement_cost

    count = min(count1, count2, count3) # count4)

  memo[key] = count

  return count

def cleanQuestion(question):
  exclude = set(string.punctuation)
  question = ''.join(ch for ch in question.lower() if ch not in exclude)

  # TODO(mburman): there's probably a better way to do this
  # It's important to maintain ordering here - multi word phrases should come
  # earlier in the list so that we can replace maximally.
  # Note: is should probably not be a bad start phrase by itself
  bad_start_phrase = [
      'how many',
      'when did', 'why did', 'where did', 'who did', 'what did'
      'when was', 'why was', 'where was', 'who was', 'what was',
      'what does',
      'name the', 'is the',
      'what', 'where', 'why', 'when', 'who', 'which', 'how', 'did', 'name',
      'does']

  # If a bad phrase is present in the beginning of a question, replace it.
  for bad_phrase in bad_start_phrase:
    bad_index = question.find(bad_phrase)
    if bad_index == 0:
      question = question.replace(bad_phrase, '', 1)
      break

  return question

def cleanAnswer(answer):
  exclude = set(string.punctuation)
  answer = ''.join(ch for ch in answer.lower() if ch not in exclude)

  return answer









########################
###### Procedural ######
########################

def makeSentenceArray(inputFile):
  f = open(inputFile, "r")
  sentences = f.readlines()
  for i in range(len(sentences)):
    sentences[i] = sentences[i].strip()
  f.close()

  sentences = filter(lambda s: len(s) > 0, sentences)
  return sentences

def isYesNoQuestion(question):
  parts = question.split()
  if parts[0].lower() == "is" or \
     parts[0].lower() == "did" or \
     parts[0].lower() == "does" or \
     parts[0].lower() == "are" or \
     parts[0].lower() == "has":
    return True
  return False

def isNoQuestion(question, answer):
  if " not " in question:
    if " not " in answer:
      return False
    else:
      return True
  else:
    return False

def processAnswer(closestSentence, question, distance, content):
  global global_entity
  yesno_answer_list = [
      'Is [entity] one of the 88 modern constellations?',
      'Is [entity] in the zodiac?',
      'Is Ptolemy credited with describing [entity]?',
      'Is [entity] a British film?',
      'Is [entity] a West Germanic language?',
      'Is [entity] an Italic language?',
      'Is [entity] a programming language?',
      'Is [entity] a romance language?',
      'Is [entity] an object oriented language?'
  ]

  question = question.lower()
  global_entity = global_entity.lower()
  for yesno in yesno_answer_list:
    yesno = yesno.lower()
    yesno = yesno.replace('[entity]', global_entity)
    content = content.lower()
    if yesno == question:
      log("ANSWERING OUR QUESTION")
      if 'constellations' in question:
        if isConstellation(content):
          return genYesAns()
        else:
          return genNoAns()
      if 'zodiac' in question:
        if 'zodiac' in content:
          return genYesAns()
        else:
          return genNoAns()
      if 'ptolemy' in question:
        if 'ptolemy' in content:
          return genYesAns()
        else:
          return genNoAns()
      if 'british' in question:
        if 'british' in content:
          return genYesAns()
        else:
          return genNoAns()
      if 'west germanic' in question:
        if 'west germanic' in content:
          return genYesAns()
        else:
          return genNoAns()
      if 'italic' in question:
        if 'italic' in content:
          return genYesAns()
        else:
          return genNoAns()
      if 'programming' in question:
        if 'programming' in content:
          return genYesAns()
        else:
          return genNoAns()
      if 'object oriented' in question:
        if 'object oriented' in content:
          return genYesAns()
        else:
          return genNoAns()
      if 'romance' in question:
        if 'romance' in content:
          return genYesAns()
        else:
          return genNoAns()

  # Doing a distance check because they could have asked a vague question which
  # makes no sense and if the distance is high, we don't just want to say
  # yes/no.... For example, for the question "Is hindi a west germanic
  # language", the answer is no but we would say yes. With this check in place,
  # we now describe what Hindi is instead of saying 'Yes'.
  if distance <= 1 and isYesNoQuestion(question):
    if isNoQuestion(question, closestSentence):
      return genNoAns()
    else:
      return genYesAns()
  else:
    return closestSentence

def computeDistances(articleFile, questionFile):
  global glob_syn_dict
  global global_entity

  f = open(articleFile)
  content = f.read()
  f.close()
  global_entity = extractEntity(content)
  # log('Entity: ' + global_entity)

  answerArray = splitIntoSentences2(articleFile)
  questionArray = makeSentenceArray(questionFile)

  for question in questionArray:
    # Remove punctuations.
    question_edited = cleanQuestion(question)

    # Find synonyms for words in question.
    question_words = question_edited.split()
    # print question_words
    for word in question_words:
      glob_syn_dict[word] = getSynonyms(word)
    # print 'Synonym Dict \n', glob_syn_dict

    # Compute best answer.
    sentenceDistance = float("infinity")
    memo = dict()
    for answer in answerArray:
      answer_edited = cleanAnswer(answer)

      count = damerauDistance(splitSentence(question_edited), splitSentence(answer_edited), memo)

      if (count < sentenceDistance):
        closestSentence = answer
        sentenceDistance = count

    answer = processAnswer(closestSentence, question, sentenceDistance, content)

    # log("-------")
    # log("Question sentence:")
    # log(question)
    # log("Answer:")
    print(answer)
    # log("Damerau distance:")
    # log(str(sentenceDistance))
    # log("-------")

    # Reset synonym dict.
    glob_syn_dict = dict()

if __name__ == '__main__':
  if len(sys.argv) < 3:
    print 'Usage: ./answer.py <article_text> <questions_text>\n'
    sys.exit(0)

  computeDistances(sys.argv[1], sys.argv[2])
