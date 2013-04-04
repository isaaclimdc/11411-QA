#!/usr/local/bin/python

import string, sys, subprocess, ntpath, os

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

def getFileName(file_path, trunc_ext):
  file_path = ntpath.basename(file_path)

  if trunc_ext:
    return file_path[:-4]
  else:
    return file_path

def getXMLFilePath(file_path):
  file_name = getFileName(file_path, False)
  xml_path = '../helpers/tmp/' + file_name + '.xml'
  return xml_path

def getOutputFilePath(output_dir, input_path):
  file_name = getFileName(input_path, True)
  output_path = output_dir + file_name + '.tag'
  return output_path

if __name__ == '__main__':
  if len(sys.argv) < 4:
    print 'Usage: ' + \
        './stanford_helper.py <input file> <output dir> <tag type>\n'
    sys.exit(0)

  input_path = sys.argv[1]
  input_path_rel = '../../test_data/' + input_path
  output_dir = sys.argv[2]
  tag_types = sys.argv[3:]

  # Execute the shell script to run StanfordCoreNLP, and wait for
  # it to complete.
  subprocess.check_call(['./parse_text.sh', input_path_rel])

  # Generate a temp xml file. For the input X.txt, generate X.txt.xml
  xml_file = getXMLFilePath(input_path)
  xml_file = open(xml_file, 'r')
  tagged_sentences = parseXMLFile(xml_file, tag_types)

  # For the input file X.txt, generate X.tags

  output_path = getOutputFilePath(output_dir, input_path)
  output_file = open(output_path, 'w+')
  output_file.write(tagged_sentences)
  output_file.close()

  # Clean up
  subprocess.check_call(['./cleanup.sh'])
