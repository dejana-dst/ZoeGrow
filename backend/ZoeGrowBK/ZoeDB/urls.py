from django.urls import path, include
from rest_framework import routers
from django.conf.urls import url
from .views import *





urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/manage/', UserAdminManageView.as_view(), name='user-manage'),
    path('plants/', PlantListView.as_view(), name='plant-list'),
    path('plantsRecommended/', PlantRecommendedView.as_view(), name='plant-list'),
 
    path('plants/<int:pk>/', PlantDetailView.as_view(), name='plant-detail'),
    path('plantCalendar/',CalendarListView.as_view(), name='calendar-list'),
    
    url(r'^plantCalendar/(?P<plant_id>\d+)/?$',CalendarDetailView.as_view(), name='calendar-detail'),
    url(r'^plantCalendar/(?P<plant_id>\d+)/events/?$',EventListView.as_view(), name='event-list'),
    url(r'^plantCalendar/(?P<plant_id>\d+)/events/(?P<event_id>\d+)/?$',EventDetailView.as_view(), name='event-detail'),
    url(r'^plantCalendar/(?P<plant_id>\d+)/eventsRecommended/?$',EventRecommendedView.as_view(), name='event-list'),
   
    path('categories/', CategoryListView.as_view(), name='category-list'),
    #path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    url(r'^categories/(?P<category_id>\d+)/?$',CategoryDetailView.as_view(), name='category-detail'),
    url(r'^categories/(?P<category_id>\d+)/threads/?$',ThreadListView.as_view(), name='thread-list'),
    url(r'^categories/(?P<category_id>\d+)/threads/(?P<thread_id>\d+)/?$',ThreadDetailView.as_view(), name='thread-detail'),
    url(r'^categories/(?P<category_id>\d+)/threads/(?P<thread_id>\d+)/posts/?$',PostsListView.as_view(), name='post-list'),
    url(r'^categories/(?P<category_id>\d+)/threads/(?P<thread_id>\d+)/posts/(?P<post_id>\d+)/?$',PostDetailView.as_view(), name='post-detail'),

]