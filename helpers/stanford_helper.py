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
  return tag

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
      tag += '/' + getTag(line, tag_types)
    elif '</token>' in line:
      break
    line = xml_file.readline()
  tagged_word = word + tag
  return (word, tagged_word)

def parseSentence(xml_file, tag_types):
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
    elif '</sentence>' in line:
      break
    line = xml_file.readline()
  return (sentence, tagged_sentence)

def parseLine(line):
  start_index = line.find('>') + 1
  end_index = line.find('<', start_index)
  return line[start_index : end_index]

def getIndex(line):
  start_index = line.find('"') + 1
  end_index = line.find('"', start_index) 
  line = line[start_index : end_index]
  return int(line) - 1

def removeTags(word):
  index = word.find('/')
  return word[:index]

def getCoreferences(xml_file, sentences):
  print "BLAH"
  #print "before",sentences
  line = xml_file.readline()
  dep = []
  initial_reference = True
  seen_one_close_coref = False
  while line != '':
    if '<mention representative="true">' in line:
      initial_reference = True
    elif '<sentence>' in line:
      sentence_index = int(getTag(line, ['sentence'])) - 1
    elif '<start>' in line:
      start_index = int(getTag(line, ['start'])) - 1
    elif '<end>' in line:
      end_index = int(getTag(line, ['end'])) - 1
      if initial_reference == True:
        ref_sentence = sentences[sentence_index]
        words = ref_sentence.split()
        reference = words[start_index : end_index]
        i = 0
        comma_index = -1
        second_comma_found = False
        while i < len(reference):
          if '/,' in reference[i] and comma_index == -1:
            comma_index = i
          elif '/,' in reference[i] and not second_comma_found:
            second_comma_found = True
          elif '/,' in reference[i]:
            reference = reference[:comma_index] + reference[i+1:]
            break
          i+=1
        for i in range(len(reference)):
          reference[i] = removeTags(reference[i])
      #seen_one_close_coref = False
   # elif '</mention>' in line:
      #if initial_reference == True:
       ## print "REFFEERRRRR"
        #ref_sentence = sentences[sentence_index]
        #print "ref sentence", ref_sentence
        ##print "start", start_index
        #print "end", end_index
        #words = ref_sentence.split()
        #reference = words[start_index : end_index]
        #for i in range(len(reference)):
        #  reference[i] = removeTags(reference[i])
        #initial_reference = False
    elif '</mention>' in line:
        if initial_reference == False:
          print reference
          sentence = sentences[sentence_index]
        
          print sentence
          words = sentence.split()
          for i in range(start_index, end_index):
            words[i] = words[i] + "/" + '%20'.join(reference)
          sentences[sentence_index] = ' '.join(words)
          print sentences[sentence_index]
        else:
          initial_reference = False
        seen_one_close_coref = False
    elif '</coreference>' in line:
      if seen_one_close_coref == True:
        break
      else:
        seen_one_close_coref = True
    line = xml_file.readline()
  #print ' '.join(words)
  #print sentences
  return sentences

def parseXMLFile(xml_file, tag_types):
  print "PARSING"
  line = xml_file.readline()
  sentences = []
  while line != '':
    if '<sentence id' in line:
      (sentence, tagged_sentence) = parseSentence(xml_file, tag_types)
      sentences.append(tagged_sentence)
      tagged_sentences = '\n'.join(sentences)
    elif '<coreference>' in line:
      print "HERE\n"
      getCoreferences(xml_file, sentences)
    line = xml_file.readline()
  tagged_sentences = '\n'.join(sentences)
  #for key, val in dependencies.iteritems():
   # print key, val
  return tagged_sentences

def getFileName(file_path, trunc_ext):
  file_path = ntpath.basename(file_path)

  if trunc_ext:
    return file_path[:-4]
  else:
    return file_path

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
