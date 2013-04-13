#!/bin/sh

echoerr() { echo "$@" 1>&2; }

echoerr '~ Starting up...'
mkdir tmp
cd ../libraries/stanford-corenlp/
echoerr '~ DONE!\n'

echoerr '~ Execute Stanford-CoreNLP java code...'
java -cp stanford-corenlp-1.3.4.jar:stanford-corenlp-1.3.4-models.jar:xom.jar:joda-time.jar:jollyday.jar -Xmx3g edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,lemma,ner -file $1 -outputDirectory ../../helpers/tmp
echoerr '~ DONE!\n'