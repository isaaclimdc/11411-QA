import operator, re
from classify import rate_sentence

# Scores to add to the confidence.
VERY_BAD_QUESTION = -1000
BAD_QUESTION = -50
BAD_ATTRIBUTE = -5

GOOD_ATTRIBUTE = -BAD_ATTRIBUTE
GOOD_QUESTION = -BAD_QUESTION
VERY_GOOD_QUESTION = -VERY_BAD_QUESTION

INITIAL_CONFIDENCE = 0

# Given a questions, generate a confidence score.
# Higher score is better
def generate_confidence(question):

  confidence = INITIAL_CONFIDENCE;

  # Generic and specific questions are very good by default. I subtract two from
  # the score to rank specific questions higher than generic questions. Also, if
  # we've generated a VERY_GOOD_QUESTION by some other means, this ensures it is
  # ranked higher than the generic and specific questions.
  if '[GENERIC]' in question:
    return VERY_GOOD_QUESTION - 2
  if '[SPECIFIC]' in question:
    return VERY_GOOD_QUESTION - 1

  # Get rid of question label.
  replace_regex = re.compile('^\[.*\]', re.IGNORECASE)
  question = replace_regex.sub('', question)
  question = question.strip()

  # Questions shouldn't start with these phrases.
  # If question starts with a bad phrase, lower the rank
  #bad_start_phrase = [
  #    'who as ', 'who of ',
  #    'did no ', 'did although ', 'did however ', 'did see ',
  #    'did follow', 'is no '
  #]
  #for bad_phrase in bad_start_phrase:
  #  bad_index = question.find(bad_phrase)
  #  if bad_index == 0:
  #    confidence += VERY_BAD_QUESTION

  rating = rate_sentence(question)

  if rating == "Good":
    confidence += VERY_GOOD_QUESTION
  elif rating == "Bad":
    confidence += VERY_BAD_QUESTION

  return confidence

def rank(questions):
  # Generate confidence scores.
  confidence_map = {}
  for question in questions:
    question = question.strip()
    confidence_map[question] = generate_confidence(question)

  # Sort into tuple (question, score).
  sorted_questions = sorted(confidence_map.iteritems(), key=operator.itemgetter(1))
  sorted_questions.reverse()
  return sorted_questions
