from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from .forms import CrawlForm
from .forms import SearchForm

def get_query(request):
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        # check whether it's valid:
        if form.is_valid():
            query_result = form.cleaned_data['query']
            print query_result
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SearchForm()

    return render(request, 'classification.html', {'form': form})

def result(request):
    return render(request, 'results.html')
def classification(request):
    return render(request, 'classification.html')
def index(request):
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

def crawl(request):
    print "Crawl waala page"
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = CrawlForm(request.GET)
        # check whether it's valid:
        if form.is_valid():
            print "Valid Form"
            for item in form.cleaned_data['crawlSelection']:
                print item
            return HttpResponseRedirect('/results/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CrawlForm()

    return render(request, 'crawl.html', {'form': form})
