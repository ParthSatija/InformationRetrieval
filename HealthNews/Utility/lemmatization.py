import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer


class lemmatization(object):
    def __init__(self):
        self.lmtzr = WordNetLemmatizer()
        self.stop_words = set(stopwords.words("english"))

    def removeStopWords(self, words):
        line = []
        for w in words:
            if w not in self.stop_words:
                line.append(w)
        return line

    def getBiwords(self, words):
        bigrams_val = nltk.bigrams(words)
        biwords = []
        for word in bigrams_val:
            biwords.append(word)
        return biwords

    def lemmatizeWord(self, lst):
        lemmatized_list = []
        for item in lst:
            lemmatized_list.append(self.lmtzr.lemmatize(item))
        return lemmatized_list
