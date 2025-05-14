from django.contrib import admin
from django.urls import path
from playerhub import views as playerhub_views
from playerhub.views import PollQuestionsListView
from users import views as users_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API endpoints - playerhub
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
    path('api/games/', playerhub_views.GameListView.as_view(), name='api-games'),
    path('api/games/<int:game_id>/',
         playerhub_views.GameView.as_view(), name='api-game'),
    path('public-api/runs/<int:pk>/',
         playerhub_views.PublicRunView.as_view(), name="public-run-detail"),
    path('public-api/runs/<int:run_id>/wipecounters/',
         playerhub_views.PublicWipecounterListView.as_view(), name="public-wipecounters-list"),
    path('public-api/runs/<int:run_id>/timers/',
         playerhub_views.PublicTimerListView.as_view(), name="public-timers-list"),

    # API endpoints - polls
    path('api/polls/create_session/',
         playerhub_views.CreatePollSessionAPIView.as_view(), name='api-polls-create'),
    path('api/polls/m/<str:client_token>/add_poll/',
         playerhub_views.PollQuestionsListView.as_view(), name='api-moderator-polls'),
    path('api/polls/m/<str:client_token>/',
         playerhub_views.PollQuestionsListView.as_view(), name='api-polls-list'),
    path('api/polls/m/<str:client_token>/delete/<str:question_id>/',
         playerhub_views.DeletePollQuestionView.as_view(), name='api-delete-poll-question'),
    path('api/polls/v/<str:client_token>/', PollQuestionsListView.as_view(), name='api-viewer-polls'),

    # API endpoints - user authorization
    path('api/register/', users_views.RegisterView.as_view(), name='api-register'),
    path('api/login/', TokenObtainPairView.as_view(), name='api-login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),

    # HTML views - user authorization
    path('login/', users_views.LoginPageView.as_view(), name='login'),
    path('register/', users_views.RegisterPageView.as_view(), name='register'),

    # HTML views - playerhub
    path('dashboard/', playerhub_views.MainDashboardView.as_view(), name='main-dashboard'),
    path('runs/create/', playerhub_views.CreateNewRunView.as_view(), name='runs-create'),
    path('runs/<int:run_id>/', playerhub_views.RunDashboardView.as_view(), name='runs-view'),
    path('runs/', playerhub_views.RunListDashboardView.as_view(), name='runs-list'),
    path('overlay/runs/<int:run_id>/', playerhub_views.OverlayRunView.as_view(), name='overlay-run'),

    # HTML views - polls
    path('polls/create/', playerhub_views.CreatePollSessionView.as_view(), name='polls-create'),
    path('polls/m/<str:moderator_token>/', playerhub_views.ModeratorPollsView.as_view(), name='polls-moderator'),
    path('polls/o/<str:overlay_token>/', playerhub_views.OverlayPollView.as_view(), name='polls-overlay'),
    path('polls/v/<str:client_token>/', playerhub_views.ViewerPollView.as_view(), name='polls-viewer'),



    # NOT USED SOLUTION - TO CLEAN UP LATER
    # # API endpoints - livehub
    # path('api/polls/mod/<str:moderator_session_code>/',
    #      livehub_views.ModeratorPollListView.as_view(), name='api-polls-moderator'),
    # path('api/polls/mod/<str:moderator_session_code>/<int:poll_id>/',
    #      livehub_views.ModeratorPollView.as_view(), name='api-poll-moderator'),
    # path('api/polls/<str:session_code>/',
    #      livehub_views.ViewerPollListView.as_view(), name='api-polls'),
    # path('api/polls/mod/<str:moderator_session_code>/<int:poll_id>/answers/',
    #      livehub_views.ModeratorAnswerListView.as_view(), name='api-answers-moderator'),
    # path('api/polls/mod/<str:moderator_session_code>/<int:poll_id>/answers/<int:answer_id>/',
    #      livehub_views.ModeratorAnswerView.as_view(), name='api-answer-moderator'),
    # path('api/polls/<str:session_code>/<int:poll_id>/answers/',
    #      livehub_views.ViewerAnswerListView.as_view(), name='api-answers'),
]
