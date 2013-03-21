#!/bin/sh
echo 'cd before'
cd ../libraries/stanford-corenlp/
echo 'java'
java -cp stanford-corenlp-1.3.4.jar:stanford-corenlp-1.3.4-models.jar:xom.jar:joda-time.jar:jollyday.jar -Xmx3g edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,lemma,ner -file $1 -outputDirectory ../../question_generator
echo 'here'
