import string, sys, subprocess

POSITION = 'POS'
NAMED_ENTITY = 'NER'
ROOT = 'lemma'

def parseWord(xml_file, tag_type):
  line = xml_file.readline()
  word_tag = '<word>'
  start_tag = '<' + tag_type + '>'
  end_tag = '</' + tag_type + '>'
  while line != '':
    if word_tag in line:
      start_index = string.find(line, word_tag) + len(word_tag)
      end_index = string.find(line, '</word>')
      word = line[start_index : end_index]
    elif start_tag in line:
      start_index = string.find(line, start_tag) + len(start_tag)
      end_index = string.find(line, end_tag)
      tag = line[start_index : end_index]
    elif '</token>' in line:
      break
    line = xml_file.readline()
  tagged_word = word + '\\' + tag
  return tagged_word

def parseSentence(xml_file, tag_type):
  line = xml_file.readline()
  words = []
  while line != '':
    if '<token id' in line:
      word = parseWord(xml_file, tag_type)
      words.append(word)
    elif '</sentence>' in line:
      break
    line = xml_file.readline()
  tagged_sentence = ' '.join(words)
  return tagged_sentence

def parseXMLFile(xml_file, parse_type):
  line = xml_file.readline()
  sentences = []
  while line != '':
    if '<sentence id' in line:
      sentence = parseSentence(xml_file, parse_type)
      sentences.append(sentence)
    line = xml_file.readline()
  tagged_sentences = ' '.join(sentences)
  return tagged_sentences

def getXMLFileLocation(file_name):
  index = file_name.rfind('/')
  name = file_name[index + 1 : ]
  xml_file = '../../question_generator/' + name + '.xml'
  return xml_file

if __name__ == '__main__':
  if len(sys.argv) < 3:
    print 'Usage: ' + \
        'python stanford_nlp_helper.py <file> <parse_type>\n'
    sys.exit(0)

  file_name = sys.argv[1]
  parse_type = sys.argv[2]

  subprocess.call(['java', '-cp', 
    'stanford-corenlp-1.3.4.jar:stanford-corenlp-1.3.4-models.jar:xom.jar:joda-time.jar:jollyday.jar', '-Xmx3g', 'edu.stanford.nlp.pipeline.StanfordCoreNLP', '-annotators' 'tokenize,ssplit,pos,lemma,ner,parse,dcoref', '-file', file_name, '-outputDirectory', '../../question_generator'])

  xml_file = getXMLFileLocation(file_name)

  xml_file = open(xml_file, 'r')
  tagged_sentences = parseXMLFile(xml_file, parse_type)
  print 'tagged ', tagged_sentences 
