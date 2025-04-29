from rest_framework import generics
from .models import Poll, Answer
from .serializers import PollSerializer, AnswerSerializer
from playerhub.models import Run
from django.shortcuts import get_object_or_404


class ModeratorPollListView(generics.ListCreateAPIView):
    serializer_class = PollSerializer

    def get_queryset(self):
        return Poll.objects.filter(
            run__moderator_session_code=self.kwargs['moderator_session_code'])

    def perform_create(self, serializer):
        run = get_object_or_404(
            Run,
            moderator_session_code=self.kwargs['moderator_session_code'])
        serializer.save(run=run)


class ModeratorPollView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PollSerializer

    def get_object(self):
        return get_object_or_404(
            Poll.objects.filter(
                run__moderator_session_code=self.kwargs['moderator_session_code']),
            id=self.kwargs['poll_id']
        )


class ViewerPollListView(generics.ListAPIView):
    serializer_class = PollSerializer

    def get_queryset(self):
        return Poll.objects.filter(
            run__session_code=self.kwargs['session_code']
        )


class ModeratorAnswerListView(generics.ListCreateAPIView):
    serializer_class = AnswerSerializer

    def get_queryset(self):
        return Answer.objects.filter(
            poll__run__moderator_session_code=self.kwargs['moderator_session_code'])

    def perform_create(self, serializer):
        poll = get_object_or_404(
            Poll,
            run__moderator_session_code=self.kwargs['moderator_session_code'])
        serializer.save(poll=poll)


class ModeratorAnswerView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AnswerSerializer

    def get_object(self):
        return get_object_or_404(
            Answer.objects.filter(
                poll__run__moderator_session_code=self.kwargs['moderator_session_code'],
                id=self.kwargs['answer_id']
            )
        )


class ViewerAnswerListView(generics.ListAPIView):
    serializer_class = AnswerSerializer

    def get_queryset(self):
        return Answer.objects.filter(
            poll__run__session_code=self.kwargs['session_code']
        )
