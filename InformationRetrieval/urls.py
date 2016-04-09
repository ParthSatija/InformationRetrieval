from django.conf.urls import include, url
from django.contrib import admin
from HealthNews import views

urlpatterns = [
    url(r'^$', views.view_index),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^classification/', views.view_classification),
    url(r'^crawl/', views.view_crawl),
]
