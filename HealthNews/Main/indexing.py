from urllib2 import urlopen
from HealthNews.Main.lemmatization import lemmatization
import pysolr, os, json
import simplejson


class Indexing(object):
    def __init__(self):
        self.solr = pysolr.Solr('http://localhost:8983/solr/test', timeout=10)
        self.lem = lemmatization()

    def delete_index(self):
        # Delete existing indexed json files in solr
        self.solr.delete(q='*:*')

    def send_file_to_Solr(self, data):
        for j in range(len(data["response"]["docs"])):
            jsondata = {}
            current_response = data["response"]["docs"][j]
            DocId = current_response["_id"].lower()
            print current_response
            jsondata["docID"] = DocId
            # checking if news desk exists
            if ('news_desk' in current_response and current_response["news_desk"] is not None):
                jsondata["news_desk"] = " ".join(
                    self.lem.lemmatizeWord(self.lem.removeStopWords(current_response["news_desk"].lower().split(" "))))

            # checking if print headline and main headline exists
            if ('headline' in current_response and current_response["headline"] is not None):
                k = current_response["headline"]
                d = dict()
                for key, value in k.iteritems():
                    d[" ".join(self.lem.lemmatizeWord(self.lem.removeStopWords(key.lower().split(" "))))] = " ".join(
                        self.lem.lemmatizeWord(self.lem.removeStopWords(value.lower().split())))
                jsondata['headline'] = d

                # checking if lead paragraph exists
            if ('lead_paragraph' in current_response and current_response["lead_paragraph"] is not None):
                jsondata["lead_paragraph"] = " ".join(self.lem.lemmatizeWord(
                    self.lem.removeStopWords(current_response["lead_paragraph"].lower().split())))

            if ('keywords' in current_response and current_response["keywords"] is not None):
                k = current_response["keywords"]
                l = []
                for x in k:
                    d = dict()
                    for key, v in x.iteritems():
                        d[" ".join(self.lem.lemmatizeWord(key.lower().split(" ")))] = " ".join(
                            self.lem.lemmatizeWord(v.lower().split(" ")))
                        # d.add(key.lower(), v.lower())
                    l.append(d)
                jsondata["keywords"] = l
            if ('multimedia' in current_response and current_response["multimedia"] is not None):
                jsondata["multimedia"] = "true"
            else:
                jsondata["multimedia"] = "false"
            print jsondata
            self.solr.add([jsondata])
        self.solr.commit()

    def search(self, query):
        # fields 'or'
        # 'http://localhost:8983/solr/test/select?q=keywords:*\:*Obesity*+keywords:*\:*Heart*&wt=json&rows=15'
        conn = urlopen(query)
        rsp = simplejson.load(conn)
        print len(rsp["response"]["docs"])
        print rsp["response"]["docs"]
        return rsp["response"]["docs"]
        # print "keywords:\n"
        # for result in rsp["response"]["docs"]:
        #    print(result)

"""
obj = Indexing()
print(obj.search("http://localhost:8983/solr/test/select?q=health&wt=json&rows=9999"))
"""
# conn = urlopen('http://localhost:8983/solr/test/select?q=keywords:*\:*Obesity*&wt=json&rows=15&fl=keywords')

# # fields 'and'
# conn = urlopen(
#     'http://localhost:8983/solr/test/select?q=%2Bheadline:*\:*Research*+%2Bkeywords:*\:*Obesity*&wt=json&rows=15')
# rsp = simplejson.load(conn)
# print "headline :\n"
# for result in rsp["response"]["docs"]:
#     print(result)
#
# # phrase + multi field query
# conn = urlopen(
#     'http://localhost:8983/solr/test/select?q=headline:*\:\"fat+stigma\"&keywords:*\:*obesity*&wt=json&rows=15')
# rsp = simplejson.load(conn)
# print "obesity research :\n"
# for result in rsp["response"]["docs"]:
#     print(result)
#
# # Multiple phrases Query
# conn = urlopen(
#     'http://localhost:8983/solr/test/select?q=headline:*\:\"is+leaving\"&headline:*\:\"obesity+research\"&wt=json&rows=15')
# rsp = simplejson.load(conn)
# print "is leaving :\n"
# for result in rsp["response"]["docs"]:
#     print(result)

"""

# If sending JSON files directly into solr

path = "../jsonFiles/"
count = 0
x = []
for i in os.listdir(path):
    if (i.endswith(".json")):
        with open(path + i) as data_file:
            #if(os.stat(data_file).st_size == 0):
            #    continue
            print(data_file.name)
            data = json.load(data_file)

"""
