__author__ = 'Parth'
from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(label='Query')
    CHOICES=[(1,'Article Search'),
             (2,'Image Search')]
    selection = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())

class CrawlForm(forms.Form):
    CHOICES=[('health','Health'),
             ('health_fitness','Health & Fitness'),
             ('health_nutrition','Health & Nutrition'),
             ('men_health','Men\'s Health'),
             ('women_health','Women\'s Health')]
    crawlSelection = forms.MultipleChoiceField(
        choices = CHOICES,
        widget  = forms.CheckboxSelectMultiple
    )

class ClassificationForm(forms.Form):
    headline=forms.CharField()
    keywords=forms.CharField()
    content=forms.CharField()

