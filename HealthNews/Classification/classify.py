# coding=utf-8
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import BernoulliNB

from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import VotingClassifier

from sklearn import feature_extraction

import string

from HealthNews.Main.lemmatization import lemmatization
from HealthNews.Utility.MySQL import MySQL


class classify(object):
    def classify_on(self, headline, keyword, content):
        headline = headline.lower()
        keyword = keyword.lower()
        content = content.lower()
        print ("The headline: ", headline)
        print ("The keyword: ", keyword)
        print ("The content: ", content)

        lem = lemmatization()
        database_name = "cz4034"
        table_name = "CZ4034_Original"
        mysql_object = MySQL()
        mysql_object.use_database(database_name)

        sql = "(SELECT lead_paragraph, news_desk, docID FROM " + table_name + " WHERE news_desk LIKE \"travel\" order by DocID asc  LIMIT 50) " \
                                                                              "UNION " \
                                                                              "(SELECT lead_paragraph, news_desk, docID FROM " + table_name + " WHERE news_desk LIKE \"dining\" order by DocID asc LIMIT 50) " \
                                                                                                                                              "UNION " \
                                                                                                                                              "(SELECT lead_paragraph, news_desk, docID FROM " + table_name + " WHERE news_desk LIKE \"Politics\" order by DocID asc LIMIT 50);"
        sql = sql.encode('utf-8')
        data = mysql_object.execute_query(sql)

        dict = []
        categ = []
        train_data = []
        for record in data:
            train_data.append(record[0])
            ca = record[1]

            if (ca.lower() == "travel"):
                categ.append('Travel')
            elif (ca.lower() == "dining"):
                categ.append('Dining')
            elif (ca.lower() == "politics"):
                categ.append('Politics')

            d = record[0].lower()
            d = d.translate(None, string.punctuation)
            d = lem.removeStopWords(d.split(" "))
            if d not in dict:
                dict.extend(d)

        dict = filter(None, list(set(dict)))

        model1 = SVC(kernel='linear', C=1, gamma=1)
        model2 = LogisticRegression()
        model3 = GaussianNB()
        model4 = MultinomialNB()
        model5 = BernoulliNB()
        model6 = RandomForestClassifier(n_estimators=50)
        model7 = BaggingClassifier(model2, n_estimators=50)
        model8 = GradientBoostingClassifier(loss='deviance', n_estimators=100)
        model9 = VotingClassifier(
            estimators=[("SVM", model1), ("LR", model2), ("Gauss", model3), ("Multinom", model4), ("Bernoulli", model5),
                        ("RandomForest", model6), ("Bagging", model7), ("GB", model8)], voting='hard')
        model10 = VotingClassifier(
            estimators=[("SVM", model1), ("LR", model2), ("Gauss", model3), ("Multinom", model4), ("Bernoulli", model5),
                        ("RandomForest", model6), ("Bagging", model7), ("GB", model8)], voting='hard',
            weights=[1, 1, 1, 1, 1, 2, 2, 0])

        cv = feature_extraction.text.CountVectorizer(vocabulary=dict)
        model_used = ["SVM", "LOGISTIC REGRESSION", "GAUSSIAN NB",
                      "MULTINOMIAL NB", "BERNOULLI NB", "RANDOM FOREST", "BAGGING", "GRADIENT",
                      "Voting", "Voting With Weights"]
        model_list = [model1, model2, model3, model4, model5, model6, model7, model8, model9, model10]

        for counter_model in range(0, len(model_list)):
            model = model_list[counter_model]
            X = cv.fit_transform(train_data).toarray()
            model.fit(X, categ)
            model.score(X, categ)
            Y = cv.fit_transform([content + headline + keyword]).toarray()
            predicted = model.predict(Y)
            print predicted
        return predicted