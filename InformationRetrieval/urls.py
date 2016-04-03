from django.conf.urls import include, url
from django.contrib import admin
from HealthNews import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^results/', views.result),
    url(r'^classification/', views.classification),
    url(r'^crawl/', views.crawl)
]
