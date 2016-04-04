from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from Utility.MySQL import MySQL
from textblob.classifiers import NaiveBayesClassifier

database_name = "CZ4034"
table_name = "CZ4034_Original"
mysql_object = MySQL()

mysql_object.use_database(database_name)

sql = "(SELECT lead_paragraph FROM " + table_name + " WHERE news_desk LIKE \"%fitness\" LIMIT 50) " \
      "UNION " \
      "(SELECT lead_paragraph FROM " + table_name + " WHERE news_desk LIKE \"health\" LIMIT 50) " \
      "UNION " \
      "(SELECT lead_paragraph FROM " + table_name + " WHERE news_desk LIKE \"women%\" LIMIT 50) " \
      "UNION " \
      "(SELECT lead_paragraph FROM " + table_name + " WHERE news_desk LIKE \"men%\" LIMIT 50) " \
      "UNION " \
      "(SELECT lead_paragraph FROM " + table_name + " WHERE news_desk LIKE \"travel\" LIMIT 50);"

sql = sql.encode('utf-8')
# print(sql)
data = mysql_object.execute_query(sql)
# print(len(data)

train_data =[]

dict = []

i = -1
for record in data:
    text = record[0]
    i=i+1
    for words in text.split(" "):
        if words not in dict:
            dict.append(words)
            #Increment in space model, i is document ID. Use it for column.
            #Use dict id number in row.