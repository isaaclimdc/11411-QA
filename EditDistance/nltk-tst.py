import nltk.data

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
fp = open("test_data/landon_donovan_ans.txt")
data = fp.read()
print '\n-----\n'.join(tokenizer.tokenize(data))
