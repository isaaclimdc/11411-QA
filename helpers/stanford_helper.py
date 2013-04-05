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
  return (word, tagged_word)

def parseSentence(xml_file, dependencies, tag_types):
  line = xml_file.readline()
  words = []
  tagged_words = []
  while line != '':
    if '<token id' in line:
      (word, tagged_word) = parseWord(xml_file, tag_types)
      words.append(word)
      tagged_words.append(tagged_word)
    elif '</tokens>' in line:
      tagged_sentence = ' '.join(tagged_words)
      sentence = ' '.join(words)
    elif '<collapsed-dependencies>' in line:
      print 'collapsed'
      getDependencies(xml_file, dependencies, sentence)
    elif '</sentence>' in line:
      break
    line = xml_file.readline()
  return (sentence, tagged_sentence)

def parseLine(line):
  start_index = line.find('>') + 1
  end_index = line.find('<', start_index)
  return line[start_index : end_index]

def getDependencies(xml_file, dependencies, sentence):
  line = xml_file.readline()
  dep = []
  while line != '':
    if '<governor ' in line:
      governor = parseLine(line)
    elif '<dependent ' in line:
      dependent = parseLine(line)
      depPair = (governor, dependent)
      dep.append(depPair)
    elif '</collapsed-dependencies>' in line:
      dependencies[sentence] = str(dep)
      break
    line = xml_file.readline()

def parseXMLFile(xml_file, tag_types):
  line = xml_file.readline()
  sentences = []
  dependencies = dict()
  print 'before'
  while line != '':
    if '<sentence id' in line:
      (sentence, tagged_sentence) = parseSentence(xml_file, dependencies, tag_types)
      sentences.append(tagged_sentence)
      tagged_sentences = '\n'.join(sentences)
    line = xml_file.readline()
  tagged_sentences = '\n'.join(sentences)
  return tagged_sentences

def getFileName(file_path, trunc_ext):
  file_path = ntpath.basename(file_path)

  if trunc_ext:
    return file_path[:-4]
  else:
    return file_path

  print 'dependencies'
  print dependencies
  return tagged_sentences

def getOutputFilePath(output_dir, input_path):
  file_name = getFileName(input_path, True)
  output_path = output_dir + file_name + '.tag'
  return output_path

def getXMLFileLocation(file_name):
  xml_file = 'tmp/' + file_name + '.xml'
  return xml_file

if __name__ == '__main__':
  if len(sys.argv) < 4:
    print 'Usage: ' + \
        './stanford_helper.py <file> <output> <tag_type>\n'
    sys.exit(0)

  input_path = sys.argv[1]
  output_dir = sys.argv[2]
  tag_types = sys.argv[3:]
  input_path_rel = '../../test_data/' + input_path

  # Execute the shell script to run StanfordCoreNLP, and wait for
  # it to complete.
  subprocess.check_call(['./parse_text.sh', input_path_rel])

  xml_file = getXMLFileLocation(input_path)

  xml_file = open(xml_file, 'r')
  tagged_sentences = parseXMLFile(xml_file, tag_types)

  # For the input file X.txt, generate X.tags

  output_path = getOutputFilePath(output_dir, input_path)
  output_file = open(output_path, 'w+')
  output_file.write(tagged_sentences)
  output_file.close()
