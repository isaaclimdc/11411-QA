import sys

soccer_files = [
    'buffon_ans.txt',
    'alex_morgan_ans.txt',
    'beckham_ans.txt',
    'iniesta_ans.txt',
    'landon_donovan_ans.txt',
    'messi_ans.txt',
    'ronaldo_ans.txt',
    'terry_ans.txt',
    'clint_dempsey_ans.txt'
]

programming_files = [
    'python_ans.txt',
    'perl_ans.txt',
    'java_ans.txt'
]

language_files = [
    'klingon_ans.txt',
    'chinses_ans.txt',
    'english_ans.txt',
    'hindi_ans.txt'
]

constellation_files = [
    'andromeda_ans.txt',
    'aries_ans.txt',
    'cancer_ans.txt',
    'gemini_ans.txt',
    'hercules_ans.txt',
    'orion_ans.txt',
    'ophiuchus_ans.txt',
    'crux_ans.txt'
]

movie_files = [
    'harry_potter_ans.txt',
    'the_linguists_ans.txt',
    'the_kings_speech_ans.txt',
    'the_artist_ans.txt',
    'slumdog_millionaire_ans.txt',
    'million_dollar_baby_ans.txt',
    'my_fair_lady_ans.txt',
    'lotr_ans.txt',
    'star_wars_ans.txt'
]

def get_common_features(list_files):
  words = []
  i = -1
  for arg in list_files:
    arg = 'test_data/' + arg
    i += 1
    file = open(arg, 'r')
    data = file.read()
    file.close()
    if i == 0:
      continue
    elif i != 1:
      new_words = []
      for word in words:
        if word in data:
          new_words.append(word)
    else:
      new_words = data.split()
    words = new_words
    words = list(set(words))
  return words

soccer_words = get_common_features(soccer_files)
print "Soccer words: \n" + str(soccer_words)
print "Soccer word length: " + str(len(soccer_words))

language_words = get_common_features(language_files)
print "Language words: \n" + str(language_words)
print "Language word length: " + str(len(language_words))

programming_words = get_common_features(programming_files)
print "Programming words: \n" + str(programming_words)
print "Programming word length: " + str(len(programming_words))

constellation_words = get_common_features(constellation_files)
print "Constellation words: \n" + str(constellation_words)
print "Constellation word length: " + str(len(constellation_words))

movie_words = get_common_features(movie_files)
print "Movie words: \n" + str(movie_words)
print "Movie word length: " + str(len(movie_words))
