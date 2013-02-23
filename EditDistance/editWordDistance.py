import sys
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
        if (s1[len1-1] == s2[len2-1]):
                count = damerauDistance(sentence1MinusOne, sentence2MinusOne, memo)
        else:
                count4 = float("infinity")
                if ((len1 > 1) and (len2 > 1)):
                        lastWordSentence1 = s1[len1-1]
                        secondLastWordSentence1 = s1[len1-2]
                        lastWordSentence2 = s2[len2-1]
                        secondLastWordSentence2 = s2[len2-2]
                        # Swapped letters
                        if ((lastWordSentence1 == secondLastWordSentence2) and
                            (lastWordSentence2 == secondLastWordSentence1)):
                                count4 = damerauDistance(s1[:len1-2],
                                                             s2[:len2-2],
                                                         memo) + 1

                count1 = damerauDistance(sentence1MinusOne,s2, memo) + 1 
                count2 = damerauDistance(s1, sentence2MinusOne, memo) + 1
                count3 = damerauDistance(sentence1MinusOne, sentence2MinusOne, memo) + 1
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


def computeDistances(questionFile, mode, outputFile, answerFile):
    answerArray = makeSentenceArray(answerFile)
    questionArray = makeSentenceArray(questionFile)
    output = open(outputFile, "w")
    for question in questionArray:
        closestAnswer = ""
        sentenceDistance = float("infinity")
        memo = dict()
        for answer in answerArray:
            count = damerauDistance(splitSentence(question), splitSentence(answer), memo)
            if (count < sentenceDistance):
                closestSentence = answer
                sentenceDistance = count
        print "Question sentence: " + question
        print "Answer sentence: " + closestSentence
        print "Damerau distance: " + str(sentenceDistance) + "\n"
        
        output.write("Question sentence: " + question + "\n")
        output.write("Answer sentence: " + closestSentence + "\n")
        output.write("Damerau distance: " + str(sentenceDistance) + "\n\n")
    output.close()

    

if __name__ == '__main__':
    computeDistances(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])
