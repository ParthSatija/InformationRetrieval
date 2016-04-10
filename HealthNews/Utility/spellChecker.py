# coding=utf-8

import re, collections, string
from sklearn.externals import joblib
import os

from HealthNews.Main.lemmatization import lemmatization
from HealthNews.Utility.MySQL import MySQL


class spellChecker(object):
    def __init__(self):
        self.NWORDS = self.train(self.words(joblib.load(os.getcwd() + "/HealthNews/Utility/DICTIONARY.spellcheck")))
        self.alphabet = 'abcdefghijklmnopqrstuvwxyz'

    def words(self, text):
        return re.findall('[a-z]+', text.lower())

    def train(self, features):
        model = collections.defaultdict(lambda: 1)
        for f in features:
            model[f] += 1
        return model

    def check_spell_train(self):
        sql = "select distinct lead_paragraph, docID from cz4034_original"
        sql = sql.encode('utf-8')
        lem = lemmatization()
        database_name = "cz4034"
        table_name = "CZ4034_Original"
        mysql_object = MySQL()
        mysql_object.use_database(database_name)
        data = mysql_object.execute_query(sql)
        dict = []
        for record in data:
            try:
                d = record[0].lower()
                d = d.translate(None, string.punctuation)
                d = lem.removeStopWords(d.split(" "))
                d = lem.lemmatizeWord(d)
                dict.extend(d)
            except:
                a = 1
        dict = filter(None, list(set(dict)))

        dict = " ".join(dict)
        print dict
        joblib.dump(dict, "DICTIONARY.spellcheck")

    def edits1(self, word):
        s = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [a + b[1:] for a, b in s if b]
        transposes = [a + b[1] + b[0] + b[2:] for a, b in s if len(b) > 1]
        replaces = [a + c + b[1:] for a, b in s for c in self.alphabet if b]
        inserts = [a + c + b for a, b in s for c in self.alphabet]
        return set(deletes + transposes + replaces + inserts)

    def known_edits2(self, word):
        return set(e2 for e1 in self.edits1(word) for e2 in self.edits1(e1) if e2 in self.NWORDS)

    def known(self, words):
        return set(w for w in words if w in self.NWORDS)

    def correct(self, sentence):
        corrected = ""
        for word in sentence.split(" "):
            candidates = self.known([word]) or self.known(self.edits1(word)) or self.known_edits2(word) or [word]
            corrected += max(candidates, key=self.NWORDS.get) + " "
        return corrected

