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
    path('runs/<int:pk>/', playerhub_views.RunView.as_view(), name='run'),

    path('runs/<int:run_id>/wipecounters/', playerhub_views.WipeCounterListView.as_view(), name='wipecounters'),
    path('runs/<int:run_id>/wipecounters/<int:wipecounter_id>/', playerhub_views.WipeCounterView.as_view(), name='wipecounter'),

    path('runs/<int:run_id>/timers/', playerhub_views.TimerListView.as_view(), name='timers'),
    path('runs/<int:run_id>/timers/<int:timer_id>/', playerhub_views.TimerView.as_view(), name='timer'),

    path('polls/mod/<str:moderator_session_code>/', livehub_views.ModeratorPollListView.as_view(), name='polls-moderator'),
    path('polls/mod/<str:moderator_session_code>/<int:poll_id>/', livehub_views.ModeratorPollView.as_view(), name='poll-moderator'),

    path('polls/<str:session_code>/', livehub_views.ViewerPollListView.as_view(), name='polls'),

    path('polls/mod/<str:moderator_session_code>/<int:poll_id>/answers/', livehub_views.ModeratorAnswerListView.as_view(), name='answers-moderator'),
    path('polls/mod/<str:moderator_session_code>/<int:poll_id>/answers/<int:answer_id>/', livehub_views.ModeratorAnswerView.as_view(), name='answer-moderator'),

    path('polls/<str:session_code>/<int:poll_id>/answers/', livehub_views.ViewerAnswerListView.as_view(), name='answers'),

]
