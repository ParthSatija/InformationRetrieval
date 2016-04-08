from django.shortcuts import render
from .forms import CrawlForm
from .forms import SearchForm
from .forms import ClassificationForm
from HealthNews.Crawl.crawl import crawl
from HealthNews.Classification.classify import classify
from .Main.indexing import Indexing
import json

def view_result(request):
    return render(request, 'results_query.html')

def view_image_result(request):
    return render(request, 'image_results_query.html')


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
                          {'form': form, 'stats': stats, 'classified': classified, 'headline': headline,
                           'keywords': keywords, 'content': content})

    else:
        form = ClassificationForm()

    return render(request, 'classification.html', {'form': form, 'stats': stats, 'classified': classified})


def view_index(request):
    print "Index waala page"
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        # check whether it's valid:
        if form.is_valid():
            indexing_obj = Indexing()
            print "Valid Form"
            query = form.cleaned_data['query']
            print query
            if int(form.cleaned_data['selection']) == 1:
                print "DO ARTICLE SEARCH"
                #Change test_search to search() and also remove test_search from Indexing class
                json_results = indexing_obj.search(query,"false")
                print json_results
                return render(request, 'results_query.html', {'results': json_results})
            else:
                print "DO IMAGE SEARCH"
                json_results=indexing_obj.search(query, "true")
                print json_results
                return render(request, 'image_results_query.html', {'results': json_results})
    else:
        form = SearchForm()

    return render(request, 'index.html', {'form': form})


def view_crawl(request):
    print "Crawl waala page"
    if request.method == 'GET':
        form = CrawlForm(request.GET)
        if form.is_valid():
            print "Valid Form"
            selection_list = form.cleaned_data['crawlSelection']
            print selection_list
            crawl_obj = crawl()
            crawl_results = crawl_obj.dynamic_crawl(selection_list)
            return render(request, 'results.html', {'results' : crawl_results})
    else:
        form = CrawlForm()

    return render(request, 'crawl.html', {'form': form})
