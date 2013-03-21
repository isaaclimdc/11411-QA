# curl -O http://nlp.stanford.edu/software/stanford-ner-2012-11-11.zip
# unzip stanford-ner-2012-11-11.zip
# mv stanford-ner-2012-11-11 libraries/stanford-ner
# rm stanford-ner-2012-11-11.zip

echo '~ Installing Stanford-CoreNLP...'
curl -O http://nlp.stanford.edu/software/stanford-corenlp-full-2012-11-12.zip
unzip stanford-corenlp-full-2012-11-12.zip
mv stanford-corenlp-full-2012-11-12 libraries/stanford-corenlp
rm stanford-corenlp-full-2012-11-12.zip 
echo '~ DONE!\n'

echo '~ Installing NodeBox Linguistics'
curl -O http://nodebox.net/code/data/media/linguistics.zip
unzip linguistics.zip
mv en libraries/en
rm linguistics.zip
echo '~ DONE!\n'