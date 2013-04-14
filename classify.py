# To use
# python classify.py train test
import sys, os, collections, re
import nltk

if len(sys.argv) < 2:
  print "Usage: python classify.py train_classifier"
  sys.exit()

train_in = open(sys.argv[1])
training_data = train_in.readlines()
train_in.close()

if True:
  prev_answer = ''
  prev_sentence = ''
  i = -1
  total = 0
  correct = 0
  mislabelled_good = 0
  bad_count = 0
  for item in training_data:
    item = item.strip()
    i = i+1
    if i % 3 == 0:
      prev_sentence = item
      tokens = nltk.word_tokenize(item)
      tag_tuples = nltk.pos_tag(tokens)
      words, tags = zip(*tag_tuples)
      prev_answer = 'Good'
      if tags.count('NNP') >= 1 and tags.count('NNS') >= 1:
        prev_answer = 'Bad'
    if i % 3 == 1:
      print prev_sentence
      print "Actual: " + item
      print "Guess: " + prev_answer
      if item == 'Bad':
        bad_count = bad_count + 1

      if item == prev_answer:
        correct = correct + 1
      elif item == 'Bad':
        mislabelled_good = mislabelled_good + 1
      total = total + 1

print "***STATS***"
print "Got " + str(correct) + " out of " + str(total) + " correct."
print "Mislabelled " + str(mislabelled_good) + " as Good out of " + str(bad_count) + " bad questions"

sys.exit()

# DEAD CODE BEYOND THIS POINT
# TRIED A NAIVE BAYES CLASSIFIER
# DID NOT WORK OUT
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
