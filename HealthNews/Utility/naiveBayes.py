from stringold import maketrans

from Utility.MySQL import MySQL
from textblob.classifiers import NaiveBayesClassifier
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

def removeStopWords(words):
    line = []
    stop_words = set(stopwords.words("english"))
    for w in words:
        if w not in stop_words:
            line.append(w)
    return line

database_name = "CZ4034"
table_name = "CZ4034_Original"
mysql_object = MySQL()

mysql_object.use_database(database_name)

sql = "(SELECT lead_paragraph, news_desk FROM " + table_name + " WHERE news_desk LIKE \"travel\" LIMIT 50) " \
      "UNION " \
      "(SELECT lead_paragraph, news_desk FROM " + table_name + " WHERE news_desk LIKE \"dining\" LIMIT 50) " \
      "UNION " \
      "(SELECT lead_paragraph, news_desk FROM " + table_name + " WHERE news_desk LIKE \"politics\" LIMIT 50) " \
      "UNION " \
      "(SELECT lead_paragraph, news_desk FROM " + table_name + " WHERE news_desk LIKE \"business\" LIMIT 50);"

sql = sql.encode('utf-8')
# print(sql)
data = mysql_object.execute_query(sql)
# print(len(data))

train_data =[]

for record in data:
    text = record[0]
    category = record[1]

    if(category.lower() == "travel"):
        category = 0
    elif(category[:5].lower() == "dining"):
        category = 1
    elif(category[:3].lower() == "politics"):
        category = 2
    elif(category.lower() == "business"):
        category = 3

    text = text.translate(None, string.punctuation)
    words = word_tokenize(text)
    text = " ".join(removeStopWords(words))
    train_data.append((text.strip().decode('utf-8'), category))

print(train_data)
classification = NaiveBayesClassifier(train_data)
print("classified")

sql = "SELECT DocID, lead_paragraph FROM " + table_name + " WHERE news_desk = \"\" AND section_name = \"\" LIMIT 500;"

data = mysql_object.execute_query(sql)

for record in data:
    doc_id = record[0]
    text = record[1]
    print(doc_id + " " + classification.classify(text.strip().decode('utf-8')))
