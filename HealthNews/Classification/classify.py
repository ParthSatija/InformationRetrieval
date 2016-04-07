# coding=utf-8
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import BernoulliNB

from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.externals import joblib
from sklearn import feature_extraction

import string,os

from HealthNews.Main.lemmatization import lemmatization
from HealthNews.Utility.MySQL import MySQL


class classify(object):
    def train_data(self):
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

        cv1 = feature_extraction.text.CountVectorizer(vocabulary=dict)
        cv2 = feature_extraction.text.TfidfVectorizer(vocabulary=dict)
        cv_list = [cv1, cv2]
        model_list = [model1, model2, model3, model4, model5, model6, model7, model8, model9, model10]
        model_used = ["SVM", "LOGISTIC REGRESSION", "GAUSSIAN NB",
                      "MULTINOMIAL NB", "BERNOULLI NB", "RANDOM FOREST", "BAGGING", "GRADIENT",
                      "Voting", "Voting With Weights"]
        cv_used = ["COUNT VECTORIZER", "TFIDF VECTORIZER"]
        joblib.dump(dict, os.getcwd()+"/model files/" + "DICTIONARY")

        for counter_model in range(0, len(model_list)):
            for counter_cv in range(0, len(cv_list)):
                model = model_list[counter_model]
                cv = cv_list[counter_cv]
                X = cv.fit_transform(train_data).toarray()
                model.fit(X, categ)
                joblib.dump(model, os.getcwd()+"/model files/"+model_used[counter_model] + "_" + cv_used[counter_cv] + ".pkl")  # Save as file

    def classification_results(self):

        # TEST DATA
        lem = lemmatization()
        database_name = "cz4034"
        table_name = "CZ4034_Original"
        mysql_object = MySQL()
        mysql_object.use_database(database_name)

        sql = "(SELECT lead_paragraph, news_desk FROM " + table_name + " WHERE news_desk LIKE \"Travel\" order by DocID desc  LIMIT 25) " \
                                                                       "UNION " \
                                                                       "(SELECT lead_paragraph, news_desk FROM " + table_name + " WHERE news_desk LIKE \"dining\" order by DocID desc LIMIT 25) " \
                                                                                                                                "UNION " \
                                                                                                                                "(SELECT lead_paragraph, news_desk FROM " + table_name + " WHERE news_desk LIKE \"Politics\" order by DocID desc LIMIT 25);"
        sql = sql.encode('utf-8')
        data = mysql_object.execute_query(sql)
        test_data = []
        test_categ = []
        for record in data:
            test_data.append(record[0])
            ca = record[1]
            if (ca.lower() == "travel"):
                test_categ.append('Travel')
            elif (ca.lower() == "dining"):
                test_categ.append('Dining')
            elif (ca.lower() == "politics"):
                test_categ.append('Politics')
        cv_used = ["COUNT VECTORIZER", "TFIDF VECTORIZER"]
        model_used = ["SVM", "LOGISTIC REGRESSION", "GAUSSIAN NB",
                      "MULTINOMIAL NB", "BERNOULLI NB", "RANDOM FOREST", "BAGGING", "GRADIENT",
                      "Voting", "Voting With Weights"]
        dict = joblib.load(os.getcwd()+"/model files/"+"DICTIONARY")
        cv1 = feature_extraction.text.CountVectorizer(vocabulary=dict)
        cv2 = feature_extraction.text.TfidfVectorizer(vocabulary=dict)
        cv_list = [cv1, cv2]
        result = []
        for counter_model in range(0, len(model_used)):
            for counter_cv in range(0, len(cv_used)):
                model = joblib.load(os.getcwd()+"/model files/"+model_used[counter_model] + "_" + cv_used[counter_cv] + ".pkl")
                cv = cv_list[counter_cv]
                Y = cv.fit_transform(test_data).toarray()
                predicted = model.predict(Y)
                j = 0
                travel = 0
                dining = 0
                politics = 0
                y_true = []
                y_pred = []
                for i in predicted:
                    if (test_categ[j] == "Travel"):
                        if (i == "Travel"):
                            travel += 1
                            y_pred.append(0)
                        elif (i == "Dining"):
                            y_pred.append(1)
                        else:
                            y_pred.append(2)
                        y_true.append(0)
                    elif (test_categ[j] == "Dining"):
                        if (i == "Dining"):
                            dining += 1
                            y_pred.append(1)
                        elif (i == "Travel"):
                            y_pred.append(0)
                        else:
                            y_pred.append(2)
                        y_true.append(1)
                    elif (test_categ[j] == "Politics"):
                        if (i == "Politics"):
                            politics += 1
                            y_pred.append(2)
                        elif (i == "Travel"):
                            y_pred.append(0)
                        else:
                            y_pred.append(1)
                        y_true.append(2)
                    j += 1
                score = precision_recall_fscore_support(y_true, y_pred, average='weighted')
                result.append([model_used[counter_model], cv_used[counter_cv], travel, dining, politics, score[0], score[1], ((score[1] * score[0] / (score[1] + score[0])) * 2),score[2], accuracy_score(y_true, y_pred)])
        return result
    def classify_on(self, headline, keyword, content):
        headline = headline.lower()
        keyword = keyword.lower()
        content = content.lower()
        print ("The headline: ", headline)
        print ("The keyword: ", keyword)
        print ("The content: ", content)

        model = joblib.load("LOGISTIC REGRESSION" + ".pkl")
        dict = joblib.load("DICTIONARY")
        cv = feature_extraction.text.CountVectorizer(vocabulary=dict)
        Y = cv.fit_transform([content + headline + keyword]).toarray()
        predicted = model.predict(Y)
        print predicted
        return predicted


#c = classify()
#c.train_data()
#c.classification_results()

#c.classify_on("green potato poisonous", "",
#              "fact sound like joke, perhaps urban legend grew dr. seuss's ''green egg ham.'' food scientist say one myth. reality green potato contain high level toxin, solanine, cause nausea, headache neurological problems")
