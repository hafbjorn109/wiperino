from django.shortcuts import render
from rest_framework import generics
from .models import Poll, Answer
from .serializers import PollSerializer, AnswerSerializer


class PollListView(generics.ListCreateAPIView):
    """
    API view to retrieve list of polls or create a new poll.
    """
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

class PollView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific poll.
    """
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

class AnswerListView(generics.ListCreateAPIView):
    """
    API view to retrieve list of answers or create a new answer.
    """
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

class AnswerView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific answer.
    """
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer