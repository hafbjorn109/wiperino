from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Run, WipeCounter, Timer
from .serializers import RunSerializer, WipeCounterSerializer, TimerSerializer
from django.shortcuts import get_object_or_404


class RunListView(generics.ListCreateAPIView):
    """
    API view to retrieve list of runs or create a new run.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RunSerializer

    def get_queryset(self):
        return Run.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RunView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific run.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RunSerializer

    def get_queryset(self):
        return Run.objects.filter(user=self.request.user)


class WipeCounterListView(generics.ListCreateAPIView):
    """
    API view to retrieve list of wipe counters or create a new wipe counter.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = WipeCounterSerializer

    def get_queryset(self):
        return WipeCounter.objects.filter(run__id = self.kwargs['run_id'], run__user=self.request.user)

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
    queryset = Timer.objects.all()
    serializer_class = TimerSerializer


class TimerView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific timer.
    """
    permission_classes = [IsAuthenticated]
    queryset = Timer.objects.all()
    serializer_class = TimerSerializer