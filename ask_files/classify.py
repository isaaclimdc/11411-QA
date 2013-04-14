# To use

import sys, os, collections, re
import nltk

# A list of bad rules.
# For example, if NNP and NNS are POS tags of the same sentence, then the rule
# is present (or) if there are two VBD rules in the same sentence, the rule
# is present.
# The rule 'NO-VBD NO-VBG NO-VBN NO-VBP NO-VBZ NO-VB' means that if no verb is in
# the sentence, it is considered bad
# The rule DIFF-3 says the rule passes if the sentence only has 3 unique tags
rules = ['VBD VBD', 'NNP NNS', 'VBD NNS', 'WRB VBD', 'NO-VBD NO-VBG NO-VBN \
    NO-VBP NO-VBZ NO-VB NO-JJ', 'MAXLEN-8 VBZ VBN', 'UNREQ-. UNREQ-, DIFF-2']

# Check if the rule is present.
def apply_rule(rule, tags):
  tags = tags[:]
  tokens = rule.split()
  for token in tokens:
    token = token.strip()
    # If NO- is in the rule, then that tag must not be present for the rule to pass.
    if 'NO-' in token:
      if token.split('-')[1] in tags:
        return False

    # To pass, aka be a good sentence, the tag count should be <= to this number
    elif 'MAXLEN-' in token:
      if len(tags) > int(token.split('-')[1]):
        return False

    elif 'DIFF-' in token:
      size = int(token.split('-')[1])
      if len(set(tags)) > size:
        return False

    elif 'UNREQ-' in token:
      if token.split('-')[1] in tags:
        # Remove all occurences of this.
        tags = filter (lambda a: a != token.split('-')[1], tags)

    # Tag must be present for the rule to pass.
    else:
      if token not in tags:
        return False
      else:
        tags.remove(token)
  # If we get to here, then the rules is present
  return True

# Rate a particular sentence as Good or Bad. Used by the ranker to rank
# sentences.
def rate_sentence(sentence):
  tokens = nltk.word_tokenize(sentence)
  tag_tuples = nltk.pos_tag(tokens)
  tags = [y for x,y in tag_tuples]
  for rule in rules:
    if apply_rule(rule, tags):
      return "Bad"
  return "Good"

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print "Usage: python classify.py train_classifier"
    sys.exit()

  print "Running..."
  train_in = open(sys.argv[1])
  training_data = train_in.readlines()
  train_in.close()

  prev_answer = ''
  prev_sentence = ''
  i = -1
  total = 0
  correct = 0
  mislabelled_good = 0
  bad_count = 0
  mislabelled_good_list = []
  rule_stats = {}
  correct_stats = {}
  prev_rule = ''
  labelled_good = []

  for rule in rules:
    rule_stats[rule]  = []

  for item in training_data:
    item = item.strip()
    i = i+1
    if i % 3 == 0:
      prev_sentence = item
      tokens = nltk.word_tokenize(item)
      tag_tuples = nltk.pos_tag(tokens)
      tags = [y for x,y in tag_tuples]
      prev_answer = 'Good'
      prev_rule = ''
      for rule in rules:
        if apply_rule(rule, tags):
          prev_answer = 'Bad'
          prev_rule = rule
          break

    if i % 3 == 1:
      #print prev_sentence
      #print "Actual: " + item
      #print "Guess: " + prev_answer
      if item == 'Bad':
        bad_count = bad_count + 1

      if item == prev_answer:
        correct = correct + 1
        if item == 'Good':
          labelled_good.append(prev_sentence)
        # Check if there was a rule that was applied
        if prev_rule != '':
          if prev_rule in correct_stats:
            correct_stats[prev_rule] = correct_stats[prev_rule] + 1
          else:
            correct_stats[prev_rule] = 1

      # Mislabelled a bad sentence as good
      elif item == 'Bad':
        mislabelled_good = mislabelled_good + 1
        mislabelled_good_list.append(prev_sentence)

      # Mislabelled a good sentence as bad
      elif item == 'Good':
        if prev_rule != '':
          rule_stats[prev_rule].append(prev_sentence)

      total = total + 1

  print "***********"
  print "***STATS***"
  print "***********"
  print "Got " + str(correct) + " out of " + str(total) + " correct."
  print "Mislabelled " + str(mislabelled_good) + " as Good out of " + str(bad_count) + " bad questions"
  print "Mislabelled these Bad sentences as Good"
  for item in mislabelled_good_list:
    print item

  print "***RULE STATS***"
  print "Here are all the good sentences labelled bad"
  for key in rule_stats:
    print "*************"
    print "Rule: " + key
    print "Mislabelled bad: " + str(len(rule_stats[key]))
    if key in correct_stats:
      print "Bad sentences that this rule helped remove " + str(correct_stats[key])
    else:
      print "ERRRRROR. This rule didn't help remove any bad sentences."

    print "*************"
    print "Here are the good sentences mislabelled bad"
    for item in rule_stats[key]:
      print item
    print ""

  print "*******************************"
  print "******ALL GOOD SENTENCES*******"
  print "*******************************"
  for sentence in labelled_good:
    print sentence

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
