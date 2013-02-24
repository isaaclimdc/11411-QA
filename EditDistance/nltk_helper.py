import nltk.data
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters

# This is not perfect
# http://stackoverflow.com/questions/14095971/how-to-tweak-the-nltk-sentence-tokenizer
def splitIntoSentences(file_name):
  tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
  fp = open(file_name)
  data = fp.read()
  print '\n-----\n'.join(tokenizer.tokenize(data))
  return tokenizer.tokenize(data)

def splitIntoSentences2(file_name):
  punkt_param = PunktParameters()
  punkt_param.abbrev_types = set(['dr', 'vs', 'mr', 'mrs', 'prof', 'inc'])
  sentence_splitter = PunktSentenceTokenizer(punkt_param)
  fp = open(file_name)
  data = fp.read()
  data = data.replace('?"', '? "').replace('!"', '! "').replace('."', '. "')

  sentences = []
  for para in data.split('\n'):
    if para:
      sentences.extend(sentence_splitter.tokenize(para))
  print '\n-----\n'.join(sentences)
  return sentences
