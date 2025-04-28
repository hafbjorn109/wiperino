from django.shortcuts import render
from rest_framework import generics
from .models import Run, WipeCounter, Timer
from .serializers import RunSerializer, WipeCounterSerializer, TimerSerializer


class RunListView(generics.ListCreateAPIView):
    """
    API view to retrieve list of runs or create a new run.
    """
    queryset = Run.objects.all()
    serializer_class = RunSerializer

class RunView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific run.
    """
    queryset = Run.objects.all()
    serializer_class = RunSerializer

class WipeCounterListView(generics.ListCreateAPIView):
    """
    API view to retrieve list of wipe counters or create a new wipe counter.
    """
    queryset = WipeCounter.objects.all()
    serializer_class = WipeCounterSerializer

class WipeCounterView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific wipe counter.
    """
    queryset = WipeCounter.objects.all()
    serializer_class = WipeCounterSerializer

class TimerListView(generics.ListCreateAPIView):
    """
    API view to retrieve list of timers or create a new timer.
    """
    queryset = Timer.objects.all()
    serializer_class = TimerSerializer

class TimerView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific timer.
    """
    queryset = Timer.objects.all()
    serializer_class = TimerSerializer