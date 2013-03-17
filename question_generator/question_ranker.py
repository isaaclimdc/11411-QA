import operator

# Scores to add to the confidence.
BAD_QUESTION = 1000
BAD_ATTRIBUTE = 5

# Given a questions, generate a confidence score.
# Lower score is better
def generate_confidence(question):
  # TODO: add various criteria to determine what makes a question bad/good

  confidence = 1;

  # Questions shouldn't start with "Who as". Label it as a bad question.
  if question.startswith("Who as"):
    confidence += BAD_QUESTION

  return confidence


def rank(questions):
  confidence_map = {}

  # Generate confidence scores.
  for question in questions:
    confidence_map[question] = generate_confidence(question)

  # Sort.
  sorted_questions = sorted(confidence_map.iteritems(), key=operator.itemgetter(1))
  return sorted_questions
