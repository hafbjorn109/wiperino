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
from users import views as users_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/runs/', playerhub_views.RunListView.as_view(), name='api-runs'),
    path('api/runs/<int:pk>/', playerhub_views.RunView.as_view(), name='api-run'),

    path('api/runs/<int:run_id>/wipecounters/',
         playerhub_views.WipeCounterListView.as_view(), name='api-wipecounters'),
    path('api/runs/<int:run_id>/wipecounters/<int:wipecounter_id>/',
         playerhub_views.WipeCounterView.as_view(), name='api-wipecounter'),

    path('api/runs/<int:run_id>/timers/',
         playerhub_views.TimerListView.as_view(), name='api-timers'),
    path('api/runs/<int:run_id>/timers/<int:timer_id>/',
         playerhub_views.TimerView.as_view(), name='api-timer'),

    path('api/polls/mod/<str:moderator_session_code>/',
         livehub_views.ModeratorPollListView.as_view(), name='api-polls-moderator'),
    path('api/polls/mod/<str:moderator_session_code>/<int:poll_id>/',
         livehub_views.ModeratorPollView.as_view(), name='api-poll-moderator'),

    path('api/polls/<str:session_code>/',
         livehub_views.ViewerPollListView.as_view(), name='api-polls'),

    path('api/polls/mod/<str:moderator_session_code>/<int:poll_id>/answers/',
         livehub_views.ModeratorAnswerListView.as_view(), name='api-answers-moderator'),
    path('api/polls/mod/<str:moderator_session_code>/<int:poll_id>/answers/<int:answer_id>/',
         livehub_views.ModeratorAnswerView.as_view(), name='api-answer-moderator'),

    path('api/polls/<str:session_code>/<int:poll_id>/answers/',
         livehub_views.ViewerAnswerListView.as_view(), name='api-answers'),

    path('api/register', users_views.RegisterView.as_view(), name='api-register'),
    path('api/login', TokenObtainPairView.as_view(), name='api-login'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='api-token-refresh'),

]
