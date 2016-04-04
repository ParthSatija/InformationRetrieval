from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from .forms import CrawlForm
from .forms import SearchForm
from .forms import ClassificationForm
from HealthNews.Crawl.crawl import crawl
from HealthNews.Classification.classify import classify

def view_result(request):
    return render(request, 'results.html')

def view_classification(request):
    print "Classification waala page"
    if request.method == 'GET':
        form = ClassificationForm(request.GET)
        if form.is_valid():
            print "Valid Form"
            headline = form.cleaned_data['headline']
            keywords = form.cleaned_data['keywords']
            content = form.cleaned_data['content']
            classify_obj = classify()
            classify_obj.classify_on(headline,keywords,content)
            return HttpResponseRedirect('/results/')

    else:
        form = ClassificationForm()

    return render(request, 'classification.html', {'form': form})



def view_index(request):
    print "Index waala page"
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        # check whether it's valid:
        if form.is_valid():
            print "Valid Form"
            query_result = form.cleaned_data['query']
            print query_result
            if form.cleaned_data['selection'] == 1:
                print "DO ARTICLE SEARCH"
            else:
                print "DO IMAGE SEARCH"
            return HttpResponseRedirect('/results/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SearchForm()

    return render(request, 'index.html', {'form': form})

def view_crawl(request):
    print "Crawl waala page"
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = CrawlForm(request.GET)
        # check whether it's valid:
        if form.is_valid():
            print "Valid Form"
            selection_list = form.cleaned_data['crawlSelection']
            print selection_list
            crawl_obj = crawl()
            crawl_obj.dynamic_crawl(selection_list)
            return HttpResponseRedirect('/results/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CrawlForm()

    return render(request, 'crawl.html', {'form': form})
