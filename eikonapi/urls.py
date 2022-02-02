from django.urls import path
from . import views
 
app_name = 'eikonapi'
urlpatterns = [
    path('news/headlines', views.NewsHeadlineView.as_view()), # news/headlines 라우팅
    path('news/stories', views.NewsStoryView.as_view()), # news/stories 라우팅
    path('data', views.DataView.as_view()), # news/stories 라우팅
    path('data/timeseries', views.TimeSeriesDataView.as_view()), # news/stories 라우팅
]
