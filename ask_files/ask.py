#!/afs/andrew.cmu.edu/usr/ysim/python-411/bin/python

import argparse, os, sys, string, re, subprocess, ntpath, nltk.data, random
from qranker import rank
from generic import makeGenericQuestions
from specific import makeSpecificQuestions
from util import *

# try:
#   from nltk.corpus import wordnet
# except:
#   checkDependencies(False)

parser = argparse.ArgumentParser(description="Ask")
parser.add_argument("--txt", help="Original txt file", required="True")
parser.add_argument("--N", help="No. of questions", required="True")
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
    log("Dependencies not installed! Installing...")
    os.chdir(os.pardir)
    subprocess.check_call(['./dep.sh'])
    os.chdir('ask_files')

if len(sys.argv) < 2:
  print 'Usage: ./ask.py <article_file>\n'
  sys.exit(0)

log("~ Importing required libraries...")
checkDependencies()
lib_path = os.path.abspath('../libraries')
sys.path.append(lib_path)

# from nltk_helper import splitIntoSentences2, getSynonyms
import en
log("~ DONE!")

#######################
###### Constants ######
#######################

WHAT_TAG = "/WHAT"
PERSON_TAG = "/PERSON"
ORGANIZATION_TAG = "/ORGANIZATION"
LOCATION_TAG = "/LOCATION"
DATE_TAG = "/DATE"
VERB_TAG_1 = "/VBD"
VERB_TAG_2 = "/VBG"
PRESENT_TENSE = "PRESENT_TENSE"
PAST_TENSE = "PAST_TENSE"


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
    elif word.startswith(','):
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
      if question_parts[i] == "``" and i != len(question_parts)-1:
        question_parts[i] = question_parts[i] + question_parts[i+1]
        question_parts = question_parts[:i+1] + question_parts[i+2:]
      i+=1
  return question_parts

def removeParenthesesInfo(sentence):
  start_index = -1
  i = 0
  while i < len(sentence):
    if sentence[i] == '(':
      start_index = i
    elif sentence[i] == ')':
      if start_index != -1:
        sentence = sentence[:start_index-1] + sentence[i+1:]
        i = start_index-1
        start_index = -1
    i+=1
  return sentence

# Determine if the line is a header like "Background"
def isHeader(line):
  # Headers will start with *** and end with ***.
  return "\*\*\*" in line

def retagWords(words, proper_entity_tags):
  for i in range(len(words)):
    word_no_tag = removeTag(words[i])
    for proper_entity in proper_entity_tags:
      proper_entity_no_tag = removeTag(proper_entity)
      if word_no_tag == proper_entity_no_tag:
        words[i] = proper_entity
  return words

def removePunctuation(question_parts):
  punctuation = ['.', ',', '?', ".'"]
  for p in punctuation:
    if question_parts[-1] == p:
      question_parts = question_parts[:-1]
    elif question_parts[-1].endswith(p):
      question_parts[-1] = question_parts[-1][:-len(p)]
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

# If we have a sentence like
# In 1902, Bob did this. and the
# index is in the second half
# of the sentence, it will find the
# index Bob is at.
def findBeginningOfSegment(words, i):
  for j in range(i, -1, -1):
    if hasTag(words[j], "/,"):
      return j+1
  return 0

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

def getHeadVerbTense(question_parts):
  headVerb = None

  for origWord in question_parts:
    try:
      word = en.verb.present(origWord)
    except:
      continue

    if en.is_verb(word):
      headVerb = origWord
      break

  if headVerb == None:
    return "NO_HEAD_VERB"

  tense = en.verb.tense(headVerb)

  if "past" in tense:
    return PAST_TENSE
  elif "present" in tense or "infinitive" in tense:
    return PRESENT_TENSE
  else:
    return None


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
    question_parts.append(words[j])

  if hasTag(words[0], WHAT_TAG):
    if question_parts > 2:
      question_parts[0] = "What"
      question_parts.pop(1)
      question_parts = ["[***What***]"] + question_parts
      print "WHAT TAG!!!!"
      question = putInQuestionFormat(question_parts)
      return question

  if containsKeyRootWords(words, ['star']):
    question_parts[0] = "What"
    question_parts = ["[What]"] + question_parts
  else:
    question_parts = ["[Who]"] + question_parts
  question = putInQuestionFormat(question_parts)
  return question

# Find sentences that we can turn into
# simple 'who' questions.
def makeWhoQuestions(sentences, retag_phrases, content):
  who_questions = []
  for sentence in sentences:
    if isHeader(sentence):
      continue
    sentence = sentence.strip()
    words = sentence.split()

    words = truncateSentence2(words)

    # Reject questions shorter than length 5
    if len(words) >= 5:
      words = retagWords(words, retag_phrases)
      if hasTag(words[0], PERSON_TAG) or hasTag(words[0], WHAT_TAG):
        # For constellations, just make What questions
        if isConstellation(content):
          question = makeWhoQuestion(words, ['What'])
        else:
          question = makeWhoQuestion(words, ['Who'])
        question = cleanQuestion(question)
        who_questions.append(question)

     # else:
     #   against_question = False
     #   comma_found = False
     #   for i in xrange(len(words)):
     #     if hasTag(words[i], '/IN') and hasTag(words[i], '/against'):
     #       against_question = True
     #     elif hasTag(words[i], '/,') and against_question:
     #       question_words = words[i + 1 : ]
            # TODO(sjoyner): We need to figure out what this word refers to as this is
            # what the question is about
     #       if hasTag(question_words[0], '/PRP'):
     #         question_words = question_words[1 : ]
     #       question = makeWhoQuestion(question_words, ['Against', 'who', 'did', 'THING'])
     #       question = cleanQuestion(question)
     #       who_questions.append(question)
     #       break
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
  log(question+"\n")
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
    if isHeader(sentence):
      continue
    words = sentence.split()
    words = fixCoreferences(words)
    #words = truncateSentence(words)
    index = -1
    # Some where questions have the format
    # In LOCATION, this event occurred
    #if len(words) > 0 and hasTag(words[0], 'In') and hasTag(words[0], '/IN'):
    #  foundLocation = False
    #  foundComma = False
    #  for i in xrange(len(words)):
    #    if hasTag(words[i], LOCATION_TAG) or hasTag(words[i], ORGANIZATION_TAG):
    #      foundLocation = True
    #    # Found a potential question
    #    elif hasTag(words[i], ','):
    #      if foundLocation:
    #        foundComma = True
    #    elif hasTag(words[i], PERSON_TAG) or hasTag(words[i], ORGANIZATION_TAG):
    #      if foundComma:
    #        index = i
    #        break
    #if index != -1:
    #  question = makeWhereDidQuestion(words, index, len(words))
    #  question = cleanQuestion(question)
    #  where_questions.append(question)
    #else:
    verb_index = -1
    found_potential_location = False
    include_in_word = False
    i = 0

    intro_part = ["[WHERE]", "Where"]
    while i < len(words):
      if hasRootWord(words[i], "in"):
        # If the next word has a location tag, then this
        # is a where question
        found_potential_location = True
      elif hasRootWord(words[i], "at") and hasRootWord(words[i+1], "the"):
        found_potential_location = True
        i+=1
      elif hasRootWord(words[i], "from"):
        found_potential_location = True
        include_in_word = True
        if hasRootWord(words[i-1], "light-year"):
          intro_part = ["[WHAT]", "What"]
      elif hasTag(words[i], "/VB") and verb_index == -1:
        verb_index = i
      elif ((hasTag(words[i], LOCATION_TAG) or hasTag(words[i], ORGANIZATION_TAG))
              and found_potential_location):
        if verb_index == -1:
          comma_found = False
          while i < len(words):
            if hasTag(words[i], "/,"):
              if not ((hasTag(words[i-1], ORGANIZATION_TAG) or
                       hasTag(words[i-1], LOCATION_TAG)) and
                      (hasTag(words[i+1], ORGANIZATION_TAG) or
                        hasTag(words[i+1], LOCATION_TAG))):
                comma_found = True
                break
            i+=1
          if not comma_found:
            break

          words = truncateSentence(words[i+1:])
          for j in range(len(words)):
            if hasTag(words[j], "/VB"):
              verb_index = j
              break
        if hasTag(words[verb_index], "/VBD") and not hasRootWord(words[verb_index], "be"):
          if hasTag(words[0], PERSON_TAG) or hasTag(words[0], LOCATION_TAG):
            question_parts = ["did"] + [words[0]]
          else:
            question_parts = ["did"] + [words[0].lower()]
          question_parts = question_parts + words[1:verb_index] + [fixTense(words[verb_index])]
        else:
          question_parts = [words[verb_index]] + words[:verb_index]
          if len(question_parts) < 2:
            i+=1
            continue
          if not (hasTag(question_parts[1], PERSON_TAG) or hasTag(question_parts[1], LOCATION_TAG)):
            question_parts[1] = question_parts[1].lower()
        if include_in_word:
          question_parts = question_parts + words[verb_index+1:i]
        else:
          question_parts = question_parts + words[verb_index+1:i-1]
        question_parts = intro_part + question_parts
        question = putInQuestionFormat(question_parts)
        where_questions.append(question)
        log("words" +  ' '.join(words) + "\n")
        log("question" + question + "\n")
        break
      elif found_potential_location:
        found_potential_location = False
      i+=1
  #found_verb = False
  #for i in xrange(start_index, end_index):
  #  if (hasTag(words[i], VERB_TAG_1) or hasTag(words[i], VERB_TAG_2)) and not found_verb:
  #    words[i] = fixTense(words[i])
  #    foundVerb = True
  #  word = removeTag(words[i])
  #  if appendToPreviousWord(word):
  #    prev_word = question_parts[-1]
  #    question_parts[-1] = prev_word + word
  #  else:
  #    question_parts.append(word)
#
#  question = putInQuestionFormat(question_parts)
  return where_questions




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
  try:
    question_parts[1] = en.verb.present(question_parts[1])
  except:
    pass
  # for i in xrange (0, len(question_parts)):
  #   try:
  #     theVerb = en.verb.present(question_parts[i])
  #   except:
  #     pass

  #   # if theVerb != None:
  #   #   syns = wordnet.synsets(theVerb)

  #   #   for s in syns:
  #   #     for l in s.lemmas:
  #   #       # log(l.name)
  #   #       if l.name != theVerb:
  #   #         theVerb = l.name
  #   #         break
  #   try:
  #     question_parts[i] = en.verb.present(theVerb)
  #   except:
  #     pass

  question_parts = truncateSentence(question_parts)

  # Join everything together.
  question_parts = ["[WHEN]", "When", "did"] + question_parts
  question = putInQuestionFormat(question_parts)

  if len(question_parts) < 4:
    return None

  return question

# Find sentences that we can turn into
# simple 'when' questions.
def makeWhenQuestions(sentences):
  # Pick out occurences of dates in the text
  r = re.compile('january|february|march|april|may|june|july|august|september|october|november|December.*', re.IGNORECASE)

  when_questions = []
  for sentence in sentences:
    sentence = sentence.strip()
    if isHeader(sentence):
      continue

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
        if question != None:
          when_questions.append(question)

  return when_questions

##########################################
######### Quote Questions ################
##########################################

def makeQuoteQuestions(tagged_sentences):
  quote_questions = []
  root_words = ['say', 'comment']
  for sentence in tagged_sentences:
    if isHeader(sentence):
      continue

    found_quote = False
    start_index = -1
    sentence = sentence.strip()
    words = sentence.split()
    for i in range(len(words)):
      if hasTag(words[i], "/``"):
        found_quote = True
        start_index = i
      elif found_quote and hasTag(words[i], "/''"):
#        log "words", words
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
        found_quote = False
  return quote_questions

########################
####### Yes/No #########
########################
def getCoreference(word):
  index = -1
  for i in range(4):
    index = word.find('/', index+1)
    if index == -1:
      break
  if index != -1:
    coref = word[index+1:]
    index = coref.find('/')
    if index != -1:
      coref = coref[:index]
    coref = coref.split('%20')
    for i in range(len(coref)):
      coref[i] = coref[i] + "/NNP/PERSON/"
  else:
    coref = []
  return coref

def fixCoreferences(question_parts):
  i = 0
  ref = dict()
  while i != len(question_parts):
    if hasTag(question_parts[i], PERSON_TAG):
      break
    elif hasTag(question_parts[i], '/PRP'):# and removeTag(question_parts[i]) != "it":
      words = getCoreference(question_parts[i])
      if len(words) != 0:
        if question_parts[i] not in ref:
          question_parts = question_parts[:i] + words + question_parts[i+1:]
          i = i + len(words)
          ref[question_parts[i]] = True
      else:
        question_parts = []
        break
    else:
      i += 1
  return question_parts

def makeYesNoQuestion(tagged_sentences, retag_phrases):
  yes_no_questions = []
  for sentence in tagged_sentences:
    if isHeader(sentence):
      continue

    words = sentence.split()
    words = retagWords(words, retag_phrases)
    sentence = ' '.join(words)
    # If there is a pronoun before a reference to a
    # person, we want to change that pronoun to
    # the actual person. If we cannot find a reference
    # the length of the returned word array will be
    # zero and we will move on to the next sentence.
    words = fixCoreferences(words)
    #log "orig sentence ", sentence
    i = 0
    is_no_question = False
    has_neg_word = False
    while i < len(words):
      if i == 0:
        index = 0
        if hasTag(words[i], "/RB") and hasTag(words[i+1], "/,"):
          words = words[i+2:]
        # This is for cases like Having missed the World Cup,
        # Bob did this. We want this to be having missed the World
        # Cup, did Bob do this, not Did having missing the World
        # Cup, Bob did this.
        wait_until_after_comma = (hasTag(words[i], "/VB") or hasTag(words[i], "/IN") or
                                  hasTag(words[i], "/WRB") or hasTag(words[i], "/RB"))
        another_comma = False
        if hasTag(words[i], "/CC"):
          break
      if wait_until_after_comma:
        if hasTag(words[i], ",") and not wait_until_after_comma:
          wait_until_after_comma = False
          index = i+1
        elif hasTag(words[i], ","):
          another_comma = True
      else:
        pre_segment = []
        if words[i].startswith("not/") or words[i].startswith("never/"):
          has_neg_word = True
        # Can make a yes/no question by moving verb
        # to the beginning of the segment.
        # Counterexample for NNS
        # The official constellation/NN boundaries/NNS, as set...
        if (hasTag(words[i], "/VBZ") or hasTag(words[i], "/VBP")
          or hasTag(words[i], "/VBD")):
          if hasTag(words[i], "/VBZ"):
            did_phrase = ["does"]
          else:
            did_phrase = ["did"]
          if words[i].startswith("were"):
            words[i] = words[i].replace("were", "was")
          #index = findBeginningOfSegment(words, i)
          pre_segment = words[ : index]
          words = words[index : ]
          i = i - index
          if not has_neg_word:
            rand = random.random()
            is_no_question = rand > 0.8
          if is_no_question:
            words = words[:i] + ["not"] + words[i:]
            i +=1
          if not (hasTag(words[0], PERSON_TAG) or
                  hasTag(words[0], ORGANIZATION_TAG) or
                  hasTag(words[0], LOCATION_TAG) or
                  hasTag(words[0], "/NNP")):
            words[0] = words[0].lower()
          if hasRootWord(words[i], "be") or (hasRootWord(words[i], "have") and hasTag(words[i+1], "/VB")):
            question_parts = pre_segment + [words[i]] + words[:i] + words[i+1:]
          elif hasRootWord(words[i], "do"):
            question_parts = pre_segment + did_phrase + words[:i] + words[i+1:]
          else:
            if not another_comma:
              words[i] = fixTense(words[i])
            question_parts = pre_segment + did_phrase + words
          for j in xrange(i+1,len(question_parts)):
            if (hasTag(question_parts[j], "/CC") #and hasTag(question_parts[j-1],'/,')
               and not (hasTag(question_parts[j+1], "/JJ") or
                        hasTag(question_parts[j-1], PERSON_TAG))):
              question_parts = question_parts[:j]
              break
          if is_no_question:
            question_parts = ['[NO]'] + question_parts
          else:
            question_parts = ['[YES]'] + question_parts
          question_parts[1] = question_parts[1].title()
          question = putInQuestionFormat(question_parts)
          yes_no_questions.append(question)
          break
      i+=1
  return yes_no_questions

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
    # Raw text file. Must tag it first (slow!)
    subprocess.check_call(['./tag_data.sh', file_path, \
      "../ask_files/tagged/", "lemma NER POS"])
    tagged_file_name = ntpath.basename(file_path)
    tagged_file_path = "tagged/" + tagged_file_name[:-4] + ".tag"
  tagged_file = open(tagged_file_path, 'r')
  sentences = tagged_file.readlines()
  tagged_file.close()
  subprocess.check_call(['rm', '-rf', '../helpers/tmp'])

  return sentences

# Final pass over a question to remove unnecessary tags.
def cleanQuestion(question):
  repls = {
      '-lrb-'  : '(',
      ' -rrb-' : ')',
      '--'     : '-',
      '-LRB-'  : '(',
      ' -RRB-' : ')'
  }
  question = reduce(lambda a, kv: a.replace(*kv), repls.iteritems(), question)
  return question

def generateQuestions(tagged_sentences, original_file):
  retag_entities = ["Aries/Aries/NNP/PERSON", "Segue/Segue/NNP/PERSON",
                    "Dementor/Dementor/NNP/PERSON" , "Dementors/Dementors/NNP/PERSON",
                    "Posh/Posh/NNP/PERSON"]

  f = open(original_file)
  content = f.read()
  f.close()

  entity = extractEntity(content)
  if isConstellation(content) or isProgrammingLanguage(content):
    print "**RETAGGING**"
    retag_entities.append(entity + '/' + WHAT_TAG)

  questions = []
  questions += makeWhoQuestions(tagged_sentences, retag_entities, content)
  questions += makeWhenQuestions(tagged_sentences)
  questions += makeWhereQuestions(tagged_sentences)
  questions += makeQuoteQuestions(tagged_sentences)
  questions += makeYesNoQuestion(tagged_sentences, retag_entities)
  with open(original_file) as f:
    content = f.read()
    generic_questions = makeGenericQuestions(content, tagged_sentences)
    if generic_questions:
      questions += generic_questions
    specific_questions = makeSpecificQuestions(content, tagged_sentences)
    questions += specific_questions

  cleaned_questions = []
  for question in questions:
    cleaned_questions.append(cleanQuestion(question))
  return cleaned_questions

def rankQuestions(questions, file_path):
  to_return = []
  ranked_questions = rank(questions)
  # Write ranked questions to a file.
  if not os.path.exists('rank'):
    os.makedirs('rank')
  rank_file = open('rank/rank_' + ntpath.basename(file_path), 'w')
  for ranked_question in ranked_questions:
    to_return.append(ranked_question[0])
    rank_file.write(str(ranked_question[1]) + " " + ranked_question[0] + '\n')
  rank_file.close()

  return to_return

# Write questions to file.
def writeQuestions(questions, file_path):
  if not os.path.exists('questions'):
    os.makedirs('questions')
  file_name = ntpath.basename(file_path)[:-3] + "txt"
  question_file = open('questions/questions_' + file_name, 'w')
  for question in questions:
    question_file.write(question+'\n')
  question_file.close()

def preprocessFile(file_path):
  relative_file_path = file_path
  file_text = open(relative_file_path, "r")
  preprocess_path = "../test_data/preprocess-" + ntpath.basename(file_path)
  relative_preprocess_path = preprocess_path
  preprocess_text = open(relative_preprocess_path, "w")
  isSoc = isSoccer(file_text.read())
  file_text.seek(0)
  i = 0
  sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
  done = False
  for line in file_text.readlines():
    if done == True:
      break
    # This is the first sentence in the article that
    # contains the birthdate information for soccer
    # players. To make sure the date gets parsed correctly
    # we change the parentheses to commas.
    if i == 3 and isSoc:
      # Weird formatting in Beckham....
      comma_index = line.find(',')
      if comma_index != -1:
        line = line[:comma_index] + line[comma_index+1:]
      obe_index = line.find('OBE')
      if obe_index != -1:
        line = line[:obe_index] + line[obe_index + len('OBE'):]
      words = line.split()
      born_start_index = -1
      born_end_index = -1
      for j in range(len(words)):
        if words[j].startswith('('):
          words[j] = words[j][1:]
          born_start_index = j
        elif words[j].endswith(')'):
          words[j] = words[j][:len(words[j])-1]
          born_end_index = j + 1
      intro_sentence = words[0:born_start_index] + words[born_end_index:]
      born_sentence = words[0:born_start_index] + ['was'] + words[born_start_index : born_end_index]
      born_sentence[len(born_sentence)-1] = born_sentence[len(born_sentence)-1] + '.'
      line = ' '.join(intro_sentence + born_sentence)
    if ("(" in line and ")" in line):
      line = removeParenthesesInfo(line)
    sentences = sent_detector.tokenize(line)
    strip_sentences = []
    for sentence in sentences:
      strip_sentence = sentence.strip()
      words = strip_sentence.split()
      if len(words) < 20:
        # We don't want to include the reference section
        if strip_sentence == "See also":
          done = True
          break
        # If the sentence doesn't end with a period or
        # another form of ending sentence punctuation,
        # it is most likely a header and we want to add
        # punctuation to distinguish the header from the
        # next sentence
        if not ((strip_sentence.endswith(".") or
                strip_sentence.endswith("!") or
                strip_sentence.endswith("?"))
                and strip_sentence != ""):
          strip_sentence = "***" + strip_sentence + "***."
        strip_sentences.append(strip_sentence)
    line = ' '.join(strip_sentences) + '\n'
    preprocess_text.write(line)
    i += 1
  file_text.close()
  preprocess_text.close()
  return relative_preprocess_path

if __name__ == '__main__':
  file_path = preprocessFile(args.txt)
  if args.tagged:
    file_path = args.tagged

  Nqns = int(args.N)

  log("~ Tagging data...")
  tagged_sentences = tagData(file_path)
  log("~ DONE!\n")

  log("~ Generating Questions...")
  questions = generateQuestions(tagged_sentences, args.txt)
  log("~ DONE!\n")

  log("~ Ranking questions...")
  ranked_questions = rankQuestions(questions, file_path)
  best_questions = ranked_questions[:Nqns]
  # ranked_questions = ranked_questions[:Nqns]
  log("~ DONE!\n")

  log("~ Printing questions to stdout...")
  for question in best_questions:
    replace_regex = re.compile('^\[.*\]', re.IGNORECASE)
    cleaned_question = replace_regex.sub('', question)
    print cleaned_question.strip()

  log("~ DONE!\n")

  # log("~ Writing questions to file...")
  # writeQuestions(questions, file_path)
  # log("~ DONE!\n")

  #END
