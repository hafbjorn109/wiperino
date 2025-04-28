from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Run, WipeCounter, Timer
from .serializers import RunSerializer, WipeCounterSerializer, TimerSerializer


class RunListView(generics.ListCreateAPIView):
    """
    API view to retrieve list of runs or create a new run.
    """
    permission_classes = [IsAuthenticated]
    queryset = Run.objects.all()
    serializer_class = RunSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RunView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific run.
    """
    permission_classes = [IsAuthenticated]
    queryset = Run.objects.all()
    serializer_class = RunSerializer


class WipeCounterListView(generics.ListCreateAPIView):
    """
    API view to retrieve list of wipe counters or create a new wipe counter.
    """
    permission_classes = [IsAuthenticated]
    queryset = WipeCounter.objects.all()
    serializer_class = WipeCounterSerializer


class WipeCounterView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific wipe counter.
    """
    permission_classes = [IsAuthenticated]
    queryset = WipeCounter.objects.all()
    serializer_class = WipeCounterSerializer


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