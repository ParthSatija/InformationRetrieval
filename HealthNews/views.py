import time
from django.shortcuts import render

from HealthNews.Classification.classify import classify
from HealthNews.Crawl.crawl import crawl
from HealthNews.Utility.spellChecker import spellChecker
from .Main.indexing import Indexing
from .forms import ClassificationForm
from .forms import CrawlForm
from .forms import SearchForm


def view_classification(request):
    print "Classification waala page"
    classification_obj = classify()
    stats = classification_obj.get_classification_stats()
    classified = ""
    if request.method == 'GET':
        form = ClassificationForm(request.GET)
        if form.is_valid():
            print "Valid Form"
            headline = form.cleaned_data['headline']
            keywords = form.cleaned_data['keywords']
            content = form.cleaned_data['content']
            classified = classification_obj.classify_on(headline, keywords, content)
            return render(request, 'classification.html',
                          {'form': form, 'stats': stats, 'classified': classified[0], 'headline': headline,
                           'keywords': keywords, 'content': content, 'time': classified[1]})

        else:
            form = ClassificationForm()

    return render(request, 'classification.html', {'form': form, 'stats': stats, 'classified': classified})


def view_index(request):
    print "Index waala page"
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        spl = spellChecker()
        form = SearchForm(request.GET)
        # check whether it's valid:
        if form.is_valid():
            indexing_obj = Indexing()
            print "Valid Form"
            query = form.cleaned_data['query']
            t0 = time.clock()
            # print query
            # print spell_check
            if int(form.cleaned_data['selection']) == 1:
                print "DO ARTICLE SEARCH"
                json_results = indexing_obj.search(query, "false")
                flag = False
                spell_check = ""
                if(len(json_results[0]) <= 10):
                    spell_check = spl.correct(query).title()
                    flag = True
                    if (spell_check.lower().strip() == query.lower().strip()):
                        flag = False
                return render(request, 'results_query.html',
                              {'results': json_results[0], 'query': query, 'query_time': round(json_results[1],3), 'suggested': spell_check, 'flag_suggested':flag})
            else:
                print "DO IMAGE SEARCH"
                json_results = indexing_obj.search(query, "true")
                flag = False
                spell_check = ""
                if(len(json_results[0]) <= 10):
                    spell_check = spl.correct(query).title()
                    flag = True
                    if (spell_check.lower().strip() == query.lower().strip()):
                        flag = False
                return render(request, 'image_results_query.html',
                              {'results': json_results[0], 'query': query, 'query_time': round(json_results[1],3), 'suggested': spell_check, 'flag_suggested':flag})
        else:
            form = SearchForm()

    return render(request, 'index.html', {'form': form})


def view_crawl(request):
    print "Crawl waala page"
    if request.method == 'GET':
        form = CrawlForm(request.GET)
        crawl_obj = crawl()
        if form.is_valid():
            if int(form.cleaned_data['selection']) == 0:
                print "Crawling by Categories"
                selection_list = form.cleaned_data['crawlSelection']
                print selection_list
                crawl_results = crawl_obj.dynamic_crawl(selection_list)
                # Modal
                return render(request, 'crawl.html', {'crawl_results': crawl_results[0], 'database_time':crawl_results[1], 'indexing_time':crawl_results[2]})
            else:
                print "Crawling by Query"
                query = form.cleaned_data['query']
                print "Query = ", query
                indexing_obj = Indexing()
                crawl_obj.crawl_by_query(query)
                crawl_results = indexing_obj.search(query, "false")
                spell_check = spellChecker().correct(query).title()
                flag = True
                if (spell_check.lower().strip() == query.lower().strip()):
                    flag = False
                # print crawl_results
                # pass Json objects similar to results
                return render(request, 'results_query.html', {'results': crawl_results[0], 'query': query, 'suggested': spell_check, 'flag_suggested':flag})
        else:
            form = CrawlForm()

    return render(request, 'crawl.html', {'form': form})
