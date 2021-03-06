# coding=utf-8
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.externals import joblib
from sklearn import feature_extraction

import string, os

from HealthNews.Main.lemmatization import lemmatization
from HealthNews.Utility.MySQL import MySQL
import time


class classify(object):
    def train_data(self):
        lem = lemmatization()
        database_name = "cz4034"
        table_name = "CZ4034_Original"
        mysql_object = MySQL()
        mysql_object.use_database(database_name)
        path = os.getcwd() + "/HealthNews/Classification/model files/"
        # path = "C:/Users/user/Documents/PyCharm Projects/InformationRetrieval/HealthNews/Classification/model files/"
        sql = "(select distinct lead_paragraph, 'Dining', docID from cz4034_original where ((headline like '%dinner%' or lead_paragraph like '%dinner%') and typeOfMaterial not in ('Blog','Biography','Schedule') and headline not like '%Super-Duper%') or news_desk like '%dining%' order by DocID asc LIMIT 300)" \
              "UNION" \
              "(select distinct lead_paragraph, 'Travel', docID from cz4034_original where ((headline  like '%flight%' or lead_paragraph like '%flight%'))	or news_desk like '%travel%' or ((headline  like '%driving%' and (headline like '%road%' or headline like '%rage%')) or (lead_paragraph like '%driving%' and (lead_paragraph like '%road%' or lead_paragraph like '%rage%'))) order by DocID asc LIMIT 300)" \
              "UNION" \
              "(select distinct lead_paragraph, 'Politics', docID from cz4034_original where news_desk not like '%politics%' and lead_paragraph like '%government%' and lead_paragraph like '%congress%' and typeOfMaterial not in ('Blog','Summary') and news_desk not in ('Magazine') order by DocID asc LIMIT 300)"
        sql = sql.encode('utf-8')
        data = mysql_object.execute_query(sql)

        dict = []
        categ = []
        train = []
        for record in data:
            train.append(record[0])
            ca = record[1]
            categ.append(ca)

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

        joblib.dump(dict, path + "DICTIONARY")

        for counter_model in range(0, len(model_list)):
            for counter_cv in range(0, len(cv_list)):
                model = model_list[counter_model]
                cv = cv_list[counter_cv]
                X = cv.fit_transform(train).toarray()
                model.fit(X, categ)
                joblib.dump(model, path + model_used[counter_model] + "_" + cv_used[
                    counter_cv] + ".pkl")  # Save as file
                print model_used[counter_model] + " done."

    def classification_results(self):

        # TEST DATA
        lem = lemmatization()
        database_name = "cz4034"
        table_name = "CZ4034_Original"
        mysql_object = MySQL()
        mysql_object.use_database(database_name)
        path = os.getcwd() + "/HealthNews/Classification/model files/"
        #       path = "C:/Users/user/Documents/PyCharm Projects/InformationRetrieval/HealthNews/Classification/model files/"
        test_sql = "(select distinct lead_paragraph, 'Dining', docID from cz4034_original where ((headline like '%dinner%' or lead_paragraph like '%dinner%') and typeOfMaterial not in ('Blog','Biography','Schedule') and headline not like '%Super-Duper%') or news_desk like '%dining%' order by DocID desc LIMIT 80)" \
                   "UNION" \
                   "(select distinct lead_paragraph, 'Travel', docID from cz4034_original where ((headline  like '%flight%' or lead_paragraph like '%flight%')) or news_desk like '%travel%' or ((headline  like '%driving%' and (headline like '%road%' or headline like '%rage%')) or (lead_paragraph like '%driving%' and (lead_paragraph like '%road%' or lead_paragraph like '%rage%'))) order by DocID desc LIMIT 80)" \
                   "UNION" \
                   "(select distinct lead_paragraph, 'Politics', docID from cz4034_original where news_desk not like '%politics%' and lead_paragraph like '%government%' and lead_paragraph like '%congress%' and typeOfMaterial not in ('Blog','Summary') and news_desk not in ('Magazine') order by DocID desc LIMIT 80)"
        test_sql = test_sql.encode('utf-8')
        data = mysql_object.execute_query(test_sql)
        test_data = []
        test_categ = []
        for record in data:
            test_data.append(record[0])
            ca = record[1]
            test_categ.append(ca)

        cv_used = ["Count VECTORIZER", "tf-idf VECTORIZER"]
        model_used = ["SVM", "LOGISTIC REGRESSION", "GAUSSIAN NB",
                      "MULTINOMIAL NB", "BERNOULLI NB", "RANDOM FOREST", "BAGGING", "GRADIENT",
                      "Voting", "Voting With Weights"]
        dict = joblib.load(path + "DICTIONARY")
        cv1 = feature_extraction.text.CountVectorizer(vocabulary=dict)
        cv2 = feature_extraction.text.TfidfVectorizer(vocabulary=dict)
        cv_list = [cv1, cv2]
        result = []
        for counter_model in range(0, len(model_used)):
            for counter_cv in range(0, len(cv_used)):
                model = joblib.load(
                    path + model_used[counter_model] + "_" + cv_used[counter_cv].replace('-', '') + ".pkl")
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
                # print("_______________________")
                # print("MODEL      :  " + model_used[counter_model])
                # print("VECTORIZER :  " + cv_used[counter_cv])
                # print("Travel     :  %d/25" % (travel))
                # print("Dining     :  %d/25" % (dining))
                # print("Politics   :  %d/23" % (politics))
                # print("Precision  :  %.5f" % (score[0]))
                # print("Recall     :  %.5f" % (score[1]))
                # print("F(1) Score :  %.5f" % ((score[1] * score[0] / (score[1] + score[0])) * 2))
                # print("F(W) Score :  %.5f" % (score[2]))
                # print("Accuracy   :  %.5f" % accuracy_score(y_true, y_pred))
                print(confusion_matrix(y_true, y_pred))
        #         result.append(
        #             [model_used[counter_model].title(), cv_used[counter_cv][:-11], travel, dining, politics,
        #              round(score[0], 3), round(score[1], 3), round(accuracy_score(y_true, y_pred), 3),
        #              round(((score[1] * score[0] / (score[1] + score[0])) * 2), 3), round(score[2], 3)])
        #         print result
        # joblib.dump(result, path + "classification_stats.txt")
        # print result
        return result

    def classify_on(self, headline, keyword, content):
        headline = headline.lower()
        keyword = keyword.lower()
        content = content.lower()
        path = os.getcwd() + "/HealthNews/Classification/model files/"
        print ("The headline: ", headline)
        print ("The keyword: ", keyword)
        print ("The content: ", content)
        t0 = time.clock()

        model = joblib.load(path + "SVM_TFIDF VECTORIZER" + ".pkl")
        dict = joblib.load(path + "DICTIONARY")
        cv = feature_extraction.text.CountVectorizer(vocabulary=dict)
        Y = cv.fit_transform([content + headline + keyword]).toarray()
        predicted = model.predict(Y)

        print predicted
        return predicted, str(round(time.clock() - t0, 3)) + " seconds"

    def get_classification_stats(self):
        try:
            path = os.getcwd() + "/HealthNews/Classification/model files/"
            stats = joblib.load(path + "classification_stats.txt")
            return stats
        except EOFError as eoferror:
            print ("Classification statistics do not exist. Creating one...")
            return self.classification_results()
        except IOError as ioerror:
            print ("Classification statistics do not exist. Creating one...")
            return self.classification_results()

# c = classify()
# c.train_data()
# c.classification_results()

# c.classify_on("green potato poisonous", "",
#              "fact sound like joke, perhaps urban legend grew dr. seuss's ''green egg ham.'' food scientist say one myth. reality green potato contain high level toxin, solanine, cause nausea, headache neurological problems")
