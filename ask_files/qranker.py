import operator, re, random
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
def generate_confidence(question, entity):

  confidence = INITIAL_CONFIDENCE;

  # Generic and specific questions are very good by default.
  # There is a hint of randomness so that we don't give out the same generic
  # questions for every article. The randomness also helps distribute these
  # questions with the questions we actually generate.
  if '[GENERIC]' in question:
    return VERY_GOOD_QUESTION + random.randint(0, 15)
  if '[SPECIFIC]' in question:
    return VERY_GOOD_QUESTION + random.randint(-10, 10)

  # Get rid of question label.
  replace_regex = re.compile('^\[.*\]', re.IGNORECASE)
  question = replace_regex.sub('', question)
  question = question.strip()

  # Questions shouldn't start with these phrases.
  # If question starts with a bad phrase, lower the rank
  bad_start_phrase = [
      'who as ', 'who of ',
      'did no ', 'did although ', 'did however ', 'did see ',
      'did follow ', 'did class ', 'is no ',
      'who [ENTITY] ', 'what [ENTITY] ', 'when [ENTITY] ', 'how [ENTITY]'
  ]

  lower_question = question.lower()
  for bad_phrase in bad_start_phrase:
    bad_phrase = bad_phrase.replace('[ENTITY]', entity.lower())
    bad_index = lower_question.find(bad_phrase)
    if bad_index == 0:
      confidence += VERY_BAD_QUESTION * 5

  bad_mid_phrase = [
      ' who wish ', ' who not ', ' : ', ' ; ', ' ? ', ' the?', ' any?', ' also?',
  ]

  for bad_phrase in bad_mid_phrase:
    bad_phrase = bad_phrase.replace('[ENTITY]', entity.lower())
    bad_index = lower_question.find(bad_phrase)
    if bad_index > 10:
      confidence += VERY_BAD_QUESTION * 5

  rating = rate_sentence(question)

  if rating == "Good":
    confidence += VERY_GOOD_QUESTION + random.randint(-30, 10)
  elif rating == "Bad":
    confidence += VERY_BAD_QUESTION
  elif rating == "Ok":
    confidence += BAD_ATTRIBUTE

  return confidence

def rank(questions, entity):
  # Generate confidence scores.
  confidence_map = {}
  for question in questions:
    question = question.strip()
    confidence_map[question] = generate_confidence(question, entity)

  # Sort into tuple (question, score).
  sorted_questions = sorted(confidence_map.iteritems(), key=operator.itemgetter(1))
  sorted_questions.reverse()
  return sorted_questions
