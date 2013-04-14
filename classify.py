# To use
# python classify.py train test
import sys, os, collections, re
import nltk

train_in = open(sys.argv[1])
training_data = train_in.readlines()
train_in.close()

#test_in = open(sys.argv[2])
#testing_data = test_in.readlines()
#test_in.close()

testing_data = training_data[-41:]
training_data = training_data[:-41]

print "Training classifier..."
pos_tags = []
prev_tags = {}
i = -1
for line in training_data:
  i = i+1
  if i % 3 == 0:
    tokens = nltk.word_tokenize(line)
    tag_tuples = nltk.pos_tag(tokens)
    words, tags = zip(*tag_tuples)
    prev_tags = {'tags': tags}
  if i % 3 == 1:
    pos_tags.append((prev_tags, line))

featuresets = [(tags, trans) for (tags, trans) in pos_tags]
train_set = featuresets
classifier = nltk.NaiveBayesClassifier.train(train_set)

print "Classifying ..."
prev_answer = ''
prev_sentence = ''
correct = 0
i = -1
for item in testing_data:
  i = i+1
  if i % 3 == 0:
    tokens = nltk.word_tokenize(item)
    tag_tuples = nltk.pos_tag(tokens)
    words, tags = zip(*tag_tuples)
    prev_answer = classifier.classify({'tags': tags})
    prev_sentence = item
  if i % 3 == 1:
    print prev_sentence
    print "Actual: " + item
    print "Guess: " + prev_answer
