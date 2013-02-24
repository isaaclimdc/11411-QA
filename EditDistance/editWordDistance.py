#!/usr/local/bin/python
# Test commit
import sys,string

INSERTION_COST = 0
DELETION_COST = 1
REPLACEMENT_COST = 1
TRANSPOSITION_COST = 1

WORD_THRESHOLD = 2

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

def splitSentence(sentence):
  s = sentence.split()
  for i in range(len(s)):
    s[i] = s[i].strip()
  return s

def cleanQuestion(question):
  exclude = set(string.punctuation)
  question = ''.join(ch for ch in question.lower() if ch not in exclude)

  #TODO(mburman): there's probably a better way to do this
  # It's important to maintain ordering here - multi word phrases should come
  # earlier in the list so that we can replace maximally.
  bad_start_phrase = [
      'how many', 'when did', 'why did',
      'what', 'where', 'why', 'when', 'who', 'how', 'did', 'name']

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
  distance_between_words = levenshteinDistance(s1[len1-1], s2[len2-1], dict())
  if (distance_between_words <= WORD_THRESHOLD):
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
       count4 = damerauDistance(s1[:len1-2], s2[:len2-2], memo) + \
             TRANSPOSITION_COST

    count1 = damerauDistance(sentence1MinusOne,s2, memo) + DELETION_COST
    count2 = damerauDistance(s1, sentence2MinusOne, memo) + INSERTION_COST
    count3 = damerauDistance(sentence1MinusOne, sentence2MinusOne, memo) + REPLACEMENT_COST

    count = min(count1, count2, count3, count4)
  memo[key] = count
  return count

def makeSentenceArray(inputFile):
	f = open(inputFile, "r")
	sentences = f.readlines()
	for i in range(len(sentences)):
		sentences[i] = sentences[i].strip()
	f.close()
	return sentences


def computeDistances(questionFile, answerFile):
  answerArray = makeSentenceArray(answerFile)
  questionArray = makeSentenceArray(questionFile)
  for question in questionArray:
      closestAnswer = ""
      sentenceDistance = float("infinity")
      memo = dict()
      for answer in answerArray:
        answer_edited = cleanAnswer(answer)
        question_edited = cleanQuestion(question)

        count = damerauDistance(splitSentence(question_edited), splitSentence(answer_edited), memo)

        if (count < sentenceDistance):
              closestSentence = answer
              sentenceDistance = count
      print "Question sentence: " + question
      print "Answer sentence: " + closestSentence
      print "Damerau distance: " + str(sentenceDistance) + "\n"


if __name__ == '__main__':
  computeDistances(sys.argv[1], sys.argv[2])
