import os
import time
import json
import requests
import datetime
from HealthNews.Main.jsonToDatabase import jsonToDatabase
from HealthNews.Main.indexing import Indexing
from HealthNews.Utility.MySQL import MySQL


class crawl:
    def __init__(self):
        print ("Instantiated")

    def dynamic_crawl(self, crawl_list):
        print "Dynamically crawling: ", crawl_list
        result = ""
        for i in crawl_list:
            result += self.dynamic_crawl_old(i) + "\n"
            #Call Indexing to add new documents to solr.
        print result
        return result
    def dynamic_crawl_old(self, crawl_term):
        database_name = "cz4034"

        mysql_object = MySQL()
        mysql_object.use_database(database_name)
        """
        Health - Health
        Health & Fitness - Health&Fitness
        Fitness & Nutrition - Health/Fitness Nutrition
        Men's & Health - Men & Health
        Women's Health - Women's Health
        """
        fq = ""
        query = ""
        if (crawl_term == "health"):
            query = "SELECT last_date,count from CRAWL_DATE WHERE news_desk='Health'"
            news_desk = "Health"
            fq = "fq=news_desk:(\"Health\")"
            file_name = "health"
        elif (crawl_term == "health_fitness"):
            query = "SELECT last_date,count from CRAWL_DATE WHERE news_desk='Health&Fitness'"
            news_desk = "Health&Fitness"
            fq = "fq=news_desk:(\"Health%26Fitness\")"
            file_name = "health_fitness"
        elif (crawl_term == "health_nutrition"):
            query = "SELECT last_date,count from CRAWL_DATE WHERE news_desk='Health / Fitness & Nutrition'"
            news_desk = "Health/Fitness Nutrition"
            fq = "fq=news_desk:(\"Health/Fitness Nutrition\")"
            file_name = "health_nutrition"
        elif (crawl_term == "men_health"):
            query = "SELECT last_date,count from CRAWL_DATE WHERE news_desk='Men & Health'"
            news_desk = "Men & Health"
            fq = "fq=news_desk:(\"Men %26 Health\")"
            file_name = "health_men_health"
        else:
            query = "SELECT last_date,count from CRAWL_DATE WHERE news_desk='Women\\'s Health'"
            news_desk = "Women's Health"
            fq = "fq=news_desk:(\"Women's Health\")"
            file_name = "health_women_health"

        print query
        query = query.encode('utf-8')
        data = mysql_object.execute_query(query)

        last_date = data[0][0]

        print(last_date + datetime.timedelta(days=1))
        last_date = last_date+ datetime.timedelta(days=1)
        count_num = data[0][1]
        JSON_FILE_NAME = "fq_" + file_name

        current_date_format = ((datetime.date.today() + datetime.timedelta(days=0)).strftime('%Y-%m-%d'))
        if ((str(last_date) == current_date_format)):
            return ("No new articles found")
        else:
            current_date = ((datetime.date.today() + datetime.timedelta(days=0)).strftime('%Y%m%d'))
            prefix = "http://api.nytimes.com/svc/search/v2/articlesearch.json"
            sort = "sort=newest"
            page = "page="
            key1 = "api-key=bc6f4a013b593ac80ff7f31de9c52b80:11:74279314"
            key2 = "api-key=a52da62103b0deaf1a70d42c8ae09038:2:74279314"
            key3 = "api-key=04f0794217e078a662116b6a4486d18e:6:74279314"
            key = key1

            url = prefix + "?&" + fq + "&" + "begin_date=" + str(
                last_date.strftime('%Y%m%d')) + "&" "end_date=" + current_date + "&" + "sort=newest" + "&" + page + str(
                0) + "&" + key
            print (url)
            resp = requests.get(url)
            hits = resp.json()["response"]["meta"]["hits"]

            pages = int(hits / 10)
            if (pages * 10 < hits):
                pages += 1
            if (pages > 0):
                json_to_database = jsonToDatabase()
                index = Indexing()
                print("Number of pages = " + str(pages))
                for i in range(0, pages):
                    url = prefix + "?&" + fq + "&" + sort + "&" + last_date.strftime(
                        '%Y%m%d') + "&" + current_date + "&" + page + str(
                        i) + "&" + key
                    resp = requests.get(url)
                    print(os.getcwd())
                    print os.path.realpath(__file__)
                    with open(os.getcwd() + "/jsonFiles/" + JSON_FILE_NAME + str(count_num) + ".json", 'w') as jsonFile:
                        json.dump(resp.json(), jsonFile)
                    print("Writing to file: " + JSON_FILE_NAME + str(count_num) + ".json")
                    print("Page = " + str(i) + " done")
                    if (count_num % 150 == 1):
                        key = key1
                    elif (count_num % 150 == 51):
                        key = key2
                    if (count_num % 150 == 101):
                        key = key3
                    count_num += 1
                    time.sleep(5)
                    with open(os.getcwd() + "/jsonFiles/" + JSON_FILE_NAME + str(count_num) + ".json", 'r') as jsonFile:
                        data = json.load(jsonFile)
                        json_to_database.add_to_database(data)
                        index.send_file_to_Solr(data)

                mysql_object.execute_query(
                    "UPDATE crawl_date set count = " + str(count_num) + " where news_desk = \"" + str(news_desk) + "\"")
                mysql_object.execute_query(
                    "UPDATE crawl_date set last_date = \"" + str(current_date_format) + "\" where news_desk = \"" + str(
                        news_desk) + "\"")
                if (hits != 1):
                    return (str(hits) + " new articles added.")
                else:
                    return (str(hits) + " new article added.")

            else:
                return ("Corpus already up to date")
