import operator

# Scores to add to the confidence.
VERY_BAD_QUESTION = -1000
BAD_QUESTION = -50
BAD_ATTRIBUTE = -5

GOOD_ATTRIBUTE = -BAD_ATTRIBUTE
GOOD_QUESTION = -BAD_QUESTION
VERY_GOOD_QUESTION = -VERY_BAD_QUESTION

INITIAL_CONFIDENCE = 0

# TODO: add various criteria to determine what makes a question bad/good
# Given a questions, generate a confidence score.
# Higher score is better
def generate_confidence(question):
  confidence = INITIAL_CONFIDENCE;
  question = question.lower()

  # Generic and specific questions are very good by default. I subtract two from
  # the score to rank specific questions higher than generic questions. Also, if
  # we've generated a VERY_GOOD_QUESTION by some other means, this ensures it is
  # ranked higher than the generic and specific questions.
  if '[generic]' in question:
    return VERY_GOOD_QUESTION - 2
  if '[specific]' in question:
    return VERY_GOOD_QUESTION - 1

  # Questions shouldn't start with these phrases.
  # If question starts with a bad phrase, lower the rank
  bad_start_phrase = [
      'who as ', 'who of '
  ]
  for bad_phrase in bad_start_phrase:
    bad_index = question.find(bad_phrase)
    if bad_index == 0:
      confidence += VERY_BAD_QUESTION

  return confidence

def rank(questions):
  # Generate confidence scores.
  confidence_map = {}
  for question in questions:
    #confidence_map[question.replace('[GENERIC]', '')] = generate_confidence(question)
    confidence_map[question] = generate_confidence(question)

  # Sort into tuple (question, score).
  sorted_questions = sorted(confidence_map.iteritems(), key=operator.itemgetter(1))
  sorted_questions.reverse()
  return sorted_questions
