from django.contrib import admin
from django.urls import path
from django.conf.urls import include
 
urlpatterns = [
    path('eikon/', include('eikonapi.urls'), name='eikonapi') # eikon 서버에 요청
]