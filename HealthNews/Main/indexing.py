from urllib2 import urlopen
from HealthNews.Main.lemmatization import lemmatization
import pysolr, os, json
import simplejson
from nltk.corpus import wordnet as wn
from itertools import chain

class Indexing(object):
    def __init__(self):
        self.solr = pysolr.Solr('http://localhost:8983/solr/test', timeout=10)
        self.lem = lemmatization()
        self.resplst=set()

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

    def exec_query(self, url):
        print ""
        conn = urlopen(url)
        rsp = simplejson.load(conn)
        print rsp
        for result in rsp["response"]["docs"]:
             print(result)
             self.resplst.add(result["docID"][0])

    def search(self, query):

        #Lemmatized query list
        queryLst = self.lem.lemmatizeWord(self.lem.removeStopWords(query.lower().split(" ")))

        ##keyword + headline AND #############################

        url="http://localhost:8983/solr/test/select?q="

        for word in queryLst:
            url+="%2Bheadline:*\:*" + word + "*+" + "%2Bkeywords:*\:*" + word + "*+"
            #url+="%2Bheadline:*\:*" + word[0].upper() + word[1:] + "*+" + "%2Bkeywords:*\:*" + word[0].upper() + word[1:] + "*+"

        url = url[:-1]
        url+="&wt=json&rows=15"
        print "url: " + url
        self.exec_query(url)

        #keyword AND search#############################

        url="http://localhost:8983/solr/test/select?q="
        for word in queryLst:
            url+="%2Bkeywords:*\:*" + word + "*+"
            #url+="%2Bkeywords:*\:*" + word[0].upper() + word[1:] + "*+"
        url = url[:-1]
        url+="&wt=json&rows=15"
        print "url: " + url
        self.exec_query(url)


        ##headline AND search #############################
        url="http://localhost:8983/solr/test/select?q="
        for word in queryLst:
            url+="%2Bheadline:*\:*" + word + "*+"
            #url+="%2Bheadline:*\:*" + word[0].upper() + word[1:] + "*+"

        url = url[:-1]
        url+="&wt=json&rows=15"
        print "url: " + url
        self.exec_query(url)

        ##leadParagragh AND search #############################

        url="http://localhost:8983/solr/test/select?q="
        for word in queryLst:
            url+="%2Blead_paragraph:*" + word + "*+"
            #url+="%2Blead_paragraph:*\:*" + word[0].upper() + word[1:] + "*+"

        url = url[:-1]
        url+="&wt=json&rows=15"
        print "url: " + url
        self.exec_query(url)

        ##keyword + headline+ lead_paragraph+news_desk OR #############################

        url="http://localhost:8983/solr/test/select?q="

        for word in queryLst:
            url+="headline:*\:*" + word + "*+" + "keywords:*\:*" + word + "*+" + "lead_paragraph:*" + word + "*+" + "news_desk:*" + word +"*+"
            #url+="headline:*\:*" + word[0].upper() + word[1:] + "*+" + "keywords:*\:*" + word[0].upper() + word[1:] + "*+" + "lead_paragraph:*" + word[0].upper() + word[1:]  + "*+" + "news_desk:*" + word[0].upper() + word[1:]  +"*+"

        url = url[:-1]
        url+="&wt=json&rows=15"
        print "url: " + url
        self.exec_query(url)

        ##phrase search in headline #############################

        url="http://localhost:8983/solr/test/select?q=headline:*\:\""
        for word in queryLst:
            url+= word + "+"
            #url+=word[0].upper() + word[1:] + "+"

        url = url[:-1]
        url+="\"&wt=json&rows=15"
        print "url: " + url
        self.exec_query(url)

        ##phrase search in lead_paragraph #############################

        url="http://localhost:8983/solr/test/select?q=lead_paragraph:\""
        for word in queryLst:
            url+= word + "+"
            #url+=word[0].upper() + word[1:] + "+"

        url = url[:-1]
        url+="\"&wt=json&rows=15"
        print "url: " + url
        self.exec_query(url)

        ## SYNONYM headline OR search


        print "New list"
        for item in queryLst:
            synonyms = wn.synsets(item)
            lst = set(chain.from_iterable([word.lemma_names() for word in synonyms]))

            url="http://localhost:8983/solr/test/select?q="
            for word in lst:
                url+="%2Bheadline:*\:*" + word + "*+"
                #url+="headline:*\:*" + word[0].upper() + word[1:] + "*+"

            url = url[:-1]
            url+="&wt=json&rows=15"
            print "url: " + url
            self.exec_query(url)

        #Return the list of docIDs of relevant documents
        return self.resplst

"""
    lem_query = lemmatization()
        queryLst = lem_query.lemmatizeWord(lem_query.removeStopWords(query.lower().split(" ")))
        synList = []
        for obj in queryLst:
            synList = wn.synsets(obj)
            for syn in synList:
                print syn

        url = "'http://localhost:8983/solr/test/select?q=%2Bheadline:*\:*Research*+%2Bkeywords:*\:*Obesity*&wt=json&rows=15'"

        conn = urlopen(query)
        rsp = simplejson.load(conn)
        print len(rsp["response"]["docs"])
        print rsp["response"]["docs"]
        return rsp["response"]["docs"]
        # print "keywords:\n"
        # for result in rsp["response"]["docs"]:
        #    print(result)

obj = Indexing()
print(obj.search("http://localhost:8983/solr/test/select?q=health&wt=json&rows=9999"))

conn = urlopen('http://localhost:8983/solr/test/select?q=keywords:*\:*Obesity*&wt=json&rows=15&fl=keywords')
url:             http://localhost:8983/solr/test/select?q=keywords:*\:*obesity*+keywords:*\:*heart*&wt=json&rows=15
# fields 'and'
conn = urlopen(
    'http://localhost:8983/solr/test/select?q=%2Bheadline:*\:*Research*+%2Bkeywords:*\:*Obesity*&wt=json&rows=15')
rsp = simplejson.load(conn)
print "headline :\n"
for result in rsp["response"]["docs"]:
    print(result)

# phrase + multi field query
conn = urlopen(
    'http://localhost:8983/solr/test/select?q=headline:*\:\"fat+stigma\"&keywords:*\:*obesity*&wt=json&rows=15')
rsp = simplejson.load(conn)
print "obesity research :\n"
for result in rsp["response"]["docs"]:
    print(result)

# Multiple phrases Query
conn = urlopen(
    'http://localhost:8983/solr/test/select?q=headline:*\:\"is+leaving\"&headline:*\:\"obesity+research\"&wt=json&rows=15')
rsp = simplejson.load(conn)
print "is leaving :\n"
for result in rsp["response"]["docs"]:
    print(result)

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
