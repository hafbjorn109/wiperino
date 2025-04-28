"""
URL configuration for wiperino project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from playerhub import views as playerhub_views
from livehub import views as livehub_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('runs/', playerhub_views.RunListView.as_view(), name='runs'),
    path('runs/<int:pk>', playerhub_views.RunView.as_view(), name='run'),
    path('wipecounters/', playerhub_views.WipeCounterListView.as_view(), name='wipecounters'),
    path('wipecounters/<int:pk>', playerhub_views.WipeCounterView.as_view(), name='wipecounter'),
    path('timers/', playerhub_views.TimerListView.as_view(), name='timers'),
    path('timers/<int:pk>', playerhub_views.TimerView.as_view(), name='timer'),
    path('polls/', livehub_views.PollListView.as_view(), name='polls'),
    path('polls/<int:pk>', livehub_views.PollView.as_view(), name='poll'),
    path('answers/', livehub_views.AnswerListView.as_view(), name='answers'),
    path('answers/<int:pk>', livehub_views.AnswerView.as_view(), name='answer'),
]
