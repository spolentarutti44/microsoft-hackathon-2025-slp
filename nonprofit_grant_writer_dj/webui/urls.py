from django.urls import path, re_path
from ui import views

urlpatterns = [
    path('', views.index, name='index'),
    path('review/', views.review, name='review'),
] 