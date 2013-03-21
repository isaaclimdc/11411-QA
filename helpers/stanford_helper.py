#!/usr/local/bin/python

import string, sys, subprocess

POSITION = 'POS'
NAMED_ENTITY = 'NER'
ROOT = 'lemma'

def hasTag(line, tag_types):
  for tag_type in tag_types:
    start_tag = '<' + tag_type + '>'
    if start_tag in line:
      return True
  return False

def getTag(line, tag_types):
  for tag_type in tag_types:
    start_tag = '<' + tag_type + '>'
    end_tag = '</' + tag_type + '>'
    if start_tag in line:
      start_index = string.find(line, start_tag) + len(start_tag)
      end_index = string.find(line, end_tag)
      tag = line[start_index : end_index]
  return '/' + tag

def parseWord(xml_file, tag_types):
  line = xml_file.readline()
  word_tag = '<word>'
  tag = ''
  while line != '':
    if word_tag in line:
      start_index = string.find(line, word_tag) + len(word_tag)
      end_index = string.find(line, '</word>')
      word = line[start_index : end_index]
    elif hasTag(line, tag_types):
      tag += getTag(line, tag_types)
    elif '</token>' in line:
      break
    line = xml_file.readline()
  tagged_word = word + tag
  return tagged_word

def parseSentence(xml_file, tag_types):
  line = xml_file.readline()
  words = []
  while line != '':
    if '<token id' in line:
      word = parseWord(xml_file, tag_types)
      words.append(word)
    elif '</sentence>' in line:
      break
    line = xml_file.readline()
  tagged_sentence = ' '.join(words)
  return tagged_sentence

def parseXMLFile(xml_file, tag_types):
  line = xml_file.readline()
  sentences = []
  while line != '':
    if '<sentence id' in line:
      sentence = parseSentence(xml_file, tag_types)
      sentences.append(sentence)
    line = xml_file.readline()
  tagged_sentences = '\n'.join(sentences)
  return tagged_sentences

def getXMLFileLocation(file_name):
  xml_file = '../ask/' + file_name + '.xml'
  return xml_file

if __name__ == '__main__':
  if len(sys.argv) < 4:
    print 'Usage: ' + \
        './stanford_helper.py <file> <output> <tag_type>\n'
    sys.exit(0)

  file_name = sys.argv[1]
  file_path_stanford = '../../helpers/' + file_name
  output_name = sys.argv[2]
  tag_types = sys.argv[3:]

#  subprocess.call(['java', '-cp', 
 #   'stanford-corenlp-1.3.4.jar:stanford-corenlp-1.3.4-models.jar:xom.jar:joda-time.jar:jollyday.jar', '-Xmx3g', 'edu.stanford.nlp.pipeline.StanfordCoreNLP', '-annotators' 'tokenize,ssplit,pos,lemma,ner', '-file', file_name, '-outputDirectory', '../../question_generator'])
  print file_name 
  subprocess.Popen(['./parse_text.sh', file_path_stanford]).wait()

  xml_file = getXMLFileLocation(file_name)

  xml_file = open(xml_file, 'r')
  tagged_sentences = parseXMLFile(xml_file, tag_types)
  
  output_file = open(output_name, 'w+')
  output_file.write(tagged_sentences)
  output_file.close()
