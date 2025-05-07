from os import TMP_MAX

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Run, WipeCounter, Timer, Game
from .serializers import RunSerializer, WipeCounterSerializer, TimerSerializer, GameSerializer
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView


class RunListView(generics.ListCreateAPIView):
    """
    API view to retrieve list of runs or create a new run.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RunSerializer

    def get_queryset(self):
        return Run.objects.filter(user=self.request.user).order_by('id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RunView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific run.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RunSerializer

    def get_queryset(self):
        return Run.objects.filter(user=self.request.user).order_by('id')


class PublicRunView(generics.RetrieveAPIView):
    """
    API view to retrieve a specific run for public use, i.e., overlays for OBS.
    """
    queryset = Run.objects.all()
    serializer_class = RunSerializer
    permission_classes = [AllowAny]


class PublicWipecounterListView(generics.ListAPIView):
    """
    API view to retrieve list of wipe counters for public use, i.e., overlays for OBS.
    """
    serializer_class = WipeCounterSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return WipeCounter.objects.filter(run__id = self.kwargs['run_id']).order_by('id')


class WipeCounterListView(generics.ListCreateAPIView):
    """
    API view to retrieve list of wipe counters or create a new wipe counter.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = WipeCounterSerializer

    def get_queryset(self):
        return WipeCounter.objects.filter(run__id = self.kwargs['run_id'], run__user=self.request.user).order_by('id')

    def perform_create(self, serializer):
        run = get_object_or_404(Run, id=self.kwargs['run_id'], user=self.request.user)
        serializer.save(run=run)


class WipeCounterView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific wipe counter.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = WipeCounterSerializer

    def get_object(self):
        return get_object_or_404(
            WipeCounter.objects.filter(
            run__id = self.kwargs['run_id'],
            run__user= self.request.user
        ), id=self.kwargs['wipecounter_id'])


class TimerListView(generics.ListCreateAPIView):
    """
    API view to retrieve list of timers or create a new timer.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TimerSerializer

    def get_queryset(self):
        return Timer.objects.filter(run__id = self.kwargs['run_id'], run__user=self.request.user)

    def perform_create(self, serializer):
        run = get_object_or_404(Run, id=self.kwargs['run_id'], user=self.request.user)
        serializer.save(run=run)


class TimerView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific timer.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TimerSerializer

    def get_object(self):
        return get_object_or_404(
            Timer.objects.filter(
            run__id = self.kwargs['run_id'],
            run__user= self.request.user
        ), id=self.kwargs['timer_id'])


class GameListView(generics.ListCreateAPIView):
    """
    API view to retrieve list of games or create a new game.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = GameSerializer
    queryset = Game.objects.all()


class GameView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific game.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = GameSerializer

    def get_object(self):
        return get_object_or_404(Game, id=self.kwargs['game_id'])


class MainDashboardView(TemplateView):
    """
    View responsible for displaying the main dashboard after user login.
    Renders the main menu.
    """
    template_name = 'playerhub/main_dashboard.html'


class CreateNewRunView(TemplateView):
    """
    View responsible for displaying the form for creating a new run.
    Renders the form for creating a new run.
    """
    template_name = 'playerhub/create_new_run.html'


class RunDashboardView(TemplateView):
    """
    View responsible for displaying the run dashboard.
    Renders the run dashboard with run details.
    """
    template_name = 'playerhub/run_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['run'] = get_object_or_404(Run, id=self.kwargs['run_id'])
        return context


class RunListDashboardView(TemplateView):
    """
    View responsible for displaying the list of runs.
    """
    template_name = 'playerhub/run_list.html'


class OverlayRunView(TemplateView):
    """
    View responsible for displaying the overlay for OBS streaming a run..
    """
    template_name = 'playerhub/overlay_run.html'