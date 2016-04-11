# coding=utf-8
import string
from urllib2 import urlopen

from HealthNews.Utility.MySQL import MySQL

from HealthNews.Main.lemmatization import lemmatization
import pysolr, os, json, sys
import simplejson
from nltk.corpus import wordnet as wn
from itertools import chain
import re


class Indexing(object):
    def __init__(self):
        self.solr = pysolr.Solr('http://localhost:8983/solr/test', timeout=10)
        self.lem = lemmatization()
        self.resplst = set()
        database_name = "cz4034"
        table_name = "CZ4034_Original"
        self.mysql_object = MySQL()
        self.mysql_object.create_database(database_name)
        self.mysql_object.use_database(database_name)
        self.qtime = 0
    def delete_index(self):
        # Delete existing indexed json files in solr
        self.solr.delete(q='*:*')

    def send_file_to_Solr(self, data, check):
        for j in range(len(data["response"]["docs"])):
            jsondata = {}
            current_response = data["response"]["docs"][j]
            DocId = current_response["_id"].lower()
            jsondata["docID"] = DocId

            sql = "select distinct docID from cz4034_original"
            sql = self.mysql_object.execute_query(sql)
            flag = True
            for id in sql:
                if (id == DocId):
                    flag = False
            if (not check or (check and flag)):
                print ("Adding to slor")
                # checking if news desk exists
                if ('news_desk' in current_response and current_response["news_desk"] is not None):
                    jsondata["news_desk"] = " ".join(
                        self.lem.lemmatizeWord(
                            self.lem.removeStopWords(current_response["news_desk"].lower().split(" "))))

                # checking if print headline and main headline exists
                if ('headline' in current_response and current_response["headline"] is not None):
                    k = current_response["headline"]
                    d = dict()
                    for key, value in k.iteritems():
                        d[" ".join(
                            self.lem.lemmatizeWord(self.lem.removeStopWords(key.lower().split(" "))))] = " ".join(
                            self.lem.lemmatizeWord(self.lem.removeStopWords(value.lower().split())))
                    jsondata['headline'] = d

                    # checking if lead paragraph exists
                if ('lead_paragraph' in current_response and current_response["lead_paragraph"] is not None):
                    jsondata["lead_paragraph"] = " ".join(self.lem.lemmatizeWord(
                        self.lem.removeStopWords(current_response["lead_paragraph"][0:1000].lower().split())))

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
                # print jsondata
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
        self.qtime+= rsp["responseHeader"]["QTime"]

    def search(self, query, image_find):
        if (image_find == "false"):
            image = ""
        else:
            image = "multimedia*\:*true*+"

        wordlst = []  # list of non negative words
        notlst = []  # list of negative words
        for word in query.split():
            print word
            if (word[0] == '-'):
                notlst.append(word[1:])
            else:
                wordlst.append(word)
        query = ' '.join(wordlst)  # query with only positive words

        # Lemmatized query list
        notlst = self.lem.lemmatizeWord(notlst)
        queryLst = self.lem.lemmatizeWord(self.lem.removeStopWords(query.lower().split(" ")))
        main_url = "http://localhost:8983/solr/test/select?q=" + image

        ##phrase search in headline #############################

        url = "http://localhost:8983/solr/test/select?q=" + image[:-1] + "&headline:*\:\""
        for word in queryLst:
            url += word + "+"
            # url+=word[0].upper() + word[1:] + "+"

        url = url[:-1]
        for word in notlst:
            url += "+-keywords:*\:*" + word + "*" + "+-headline:*\:*" + word + "*" + "+-lead_paragraph:*\:*" + word + "*" + "+-news_desk:*\:*" + word + "*"
        url += "\"&wt=json&rows=15"
        print "url: " + url
        self.exec_query(url)

        ##phrase search in lead_paragraph #############################

        url = "http://localhost:8983/solr/test/select?q=" + image[:-1] +"&lead_paragraph:\""
        for word in queryLst:
            url += word + "+"
            # url+=word[0].upper() + word[1:] + "+"

        url = url[:-1]
        for word in notlst:
            url += "+-keywords:*\:*" + word + "*" + "+-headline:*\:*" + word + "*" + "+-lead_paragraph:*\:*" + word + "*" + "+-news_desk:*\:*" + word + "*"
        url += "\"&wt=json&rows=15"
        print "url: " + url
        self.exec_query(url)

        ##keyword + headline AND #############################
        url = main_url

        for word in queryLst:
            url += "%2Bheadline:*\:*" + word + "*+" + "%2Bkeywords:*\:*" + word + "*+"
            # url+="%2Bheadline:*\:*" + word[0].upper() + word[1:] + "*+" + "%2Bkeywords:*\:*" + word[0].upper() + word[1:] + "*+"

        url = url[:-1]
        for word in notlst:
            url += "+-keywords:*\:*" + word + "*" + "+-headline:*\:*" + word + "*" + "+-lead_paragraph:*\:*" + word + "*" + "+-news_desk:*\:*" + word + "*"
        url += "&wt=json&rows=30"
        print "url: " + url
        self.exec_query(url)

        ##headline AND search #############################
        url = main_url
        for word in queryLst:
            url += "%2Bheadline:*\:*" + word + "*+"
            # url+="%2Bheadline:*\:*" + word[0].upper() + word[1:] + "*+"

        url = url[:-1]
        for word in notlst:
            url += "+-keywords:*\:*" + word + "*" + "+-headline:*\:*" + word + "*" + "+-lead_paragraph:*\:*" + word + "*" + "+-news_desk:*\:*" + word + "*"
        url += "&wt=json&rows=15"
        print "url: " + url
        self.exec_query(url)

        ##leadParagragh AND search #############################
        url = main_url
        for word in queryLst:
            url += "%2Blead_paragraph:*" + word + "*+"
            # url+="%2Blead_paragraph:*\:*" + word[0].upper() + word[1:] + "*+"

        url = url[:-1]
        for word in notlst:
            url += "+-keywords:*\:*" + word + "*" + "+-headline:*\:*" + word + "*" + "+-lead_paragraph:*\:*" + word + "*" + "+-news_desk:*\:*" + word + "*"
        url += "&wt=json&rows=15"
        print "url: " + url
        self.exec_query(url)

        # keyword AND search#############################
        url = main_url
        for word in queryLst:
            url += "%2Bkeywords:*\:*" + word + "*+"
            # url+="%2Bkeywords:*\:*" + word[0].upper() + word[1:] + "*+"
        url = url[:-1]
        for word in notlst:
            url += "+-keywords:*\:*" + word + "*" + "+-headline:*\:*" + word + "*" + "+-lead_paragraph:*\:*" + word + "*" + "+-news_desk:*\:*" + word + "*"
        url += "&wt=json&rows=15"
        print "url: " + url
        self.exec_query(url)

        ##keyword + headline + lead_paragraph+news_desk OR #############################
        url = main_url

        for word in queryLst:
            url += "headline:*\:*" + word + "*+" + "keywords:*\:*" + word + "*+" + "lead_paragraph:*" + word + "*+" + "news_desk:*" + word + "*+"
            # url+="headline:*\:*" + word[0].upper() + word[1:] + "*+" + "keywords:*\:*" + word[0].upper() + word[1:] + "*+" + "lead_paragraph:*" + word[0].upper() + word[1:]  + "*+" + "news_desk:*" + word[0].upper() + word[1:]  +"*+"

        url = url[:-1]
        for word in notlst:
            url += "+-keywords:*\:*" + word + "*" + "+-headline:*\:*" + word + "*" + "+-lead_paragraph:*\:*" + word + "*" + "+-news_desk:*\:*" + word + "*"
        url += "&wt=json&rows=15"
        print "url: " + url
        self.exec_query(url)

        ## SYNONYM headline OR search
        for item in queryLst:
            synonyms = wn.synsets(item)
            lst = set(chain.from_iterable([word.lemma_names() for word in synonyms]))

            url = main_url
            for word in lst:
                url += "%2Bheadline:*\:*" + word + "*+"
                # url+="headline:*\:*" + word[0].upper() + word[1:] + "*+"

            url = url[:-1]
            for word in notlst:
                url += "+-keywords:*\:*" + word + "*" + "+-headline:*\:*" + word + "*" + "+-lead_paragraph:*\:*" + word + "*" + "+-news_desk:*\:*" + word + "*"
            url += "&wt=json&rows=15"
            print "url: " + url
            self.exec_query(url)

            print len(self.resplst)
            # Return data from db for the list of docIDs of relevant documents
            return self.get_data_from_db(self.resplst, image_find), self.qtime

    def get_data_from_db(self, resplst, image):
        doc_ids = ""
        for item in resplst:
            doc_ids = doc_ids + "'" + item + "',"
        if (len(doc_ids) != 0):
            doc_ids = doc_ids[:-1]
            if (image == "true"):
                sql = "select distinct typeOfMaterial, word_count, publication_date, printheadline, headline, lead_paragraph, web_url, image_url, docID from cz4034_original where docID in (" + doc_ids + ") and image_url != \"null\" order by publication_date desc;"
            else:
                sql = "select distinct typeOfMaterial, word_count, publication_date, printheadline, headline, lead_paragraph, web_url, image_url, docID from cz4034_original where docID in (" + doc_ids + ") order by publication_date desc;"
            print sql
            data = self.mysql_object.execute_query(sql)
            print len(data)
            res = []
            if (data is not None):
                for record in data:
                    dict = {}
                    type_of_material = record[0]
                    word_count = record[1]
                    pub_date = record[2][0:10]
                    printheadline = record[3]
                    headline = record[4]
                    lead_paragraph = record[5]
                    web_url = record[6]
                    image_url = record[7]
                    dict["type_of_material"] = type_of_material
                    dict["word_count"] = word_count
                    dict["pub_date"] = pub_date
                    dict["printheadline"] = printheadline
                    dict["headline"] = headline
                    dict["lead_paragraph"] = lead_paragraph
                    dict["web_url"] = web_url
                    dict["image_url"] = image_url
                    res.append(dict)
                # print res
                d = {}
                d["docs"] = res
            else:
                d = {}
                d["docs"] = []
            return json.dumps(d)
        else:
            d = {}
            d["docs"] = []
            return json.dumps(d)

# path = "../Crawl/jsonFiles/"
# count = 0
# x = []
# index = Indexing()
# index.delete_index()
# # print(os.listdir(path))
# for i in os.listdir(path):
#     if (i.endswith(".json")):
#         with open(path + i) as data_file:
#             # if(os.stat(data_file).st_size == 0):
#             #    continue
#             print(data_file.name)
#             data = json.load(data_file)
#             try:
#                 index.send_file_to_Solr(data)
#             except:
#                 print("ERROR")

# i = Indexing()
# i.search("health","true")
