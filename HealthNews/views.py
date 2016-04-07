from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import CrawlForm
from .forms import SearchForm
from .forms import ClassificationForm
from HealthNews.Crawl.crawl import crawl
from HealthNews.Classification.classify import classify
from .Main.indexing import Indexing


def view_result(request):
    return render(request, 'results_query.html')


def view_classification(request):
    print "Classification waala page"
    classification_obj = classify()
    stats = classification_obj.get_classification_stats()
    if request.method == 'GET':
        form = ClassificationForm(request.GET)
        if form.is_valid():
            print "Valid Form"
            headline = form.cleaned_data['headline']
            keywords = form.cleaned_data['keywords']
            content = form.cleaned_data['content']
            classified = classification_obj.classify_on(headline, keywords, content)
            return render(request, 'classification.html', {'form': form, 'stats': stats, 'classified': classified})

    else:
        form = ClassificationForm()

    return render(request, 'classification.html', {'form': form, 'stats': stats})


def view_index(request):
    print "Index waala page"
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        # check whether it's valid:
        if form.is_valid():
            print "Valid Form"
            query = form.cleaned_data['query']
            print query
            if int(form.cleaned_data['selection']) == 1:
                print "DO ARTICLE SEARCH"
                indexing_obj = Indexing()
                #Change test_search to search() and also remove test_search from Indexing class
                json_results = indexing_obj.test_search(query)
                return render(request, 'results_query.html', {'results': json_results})
            else:
                print "DO IMAGE SEARCH"
                return HttpResponseRedirect('/results/')
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
            crawl_obj.dynamic_crawl(selection_list)
            return HttpResponseRedirect('/results/')
    else:
        form = CrawlForm()

    return render(request, 'crawl.html', {'form': form})
