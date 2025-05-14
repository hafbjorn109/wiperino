import uuid
import json
import redis
from django.conf import settings
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Run, WipeCounter, Timer, Game
from .serializers import RunSerializer, WipeCounterSerializer, TimerSerializer, GameSerializer, \
    CreatePollSessionSerializer, PollQuestionSerializer, ErrorResponseSerializer, SuccessResponseSerializer
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


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


class PublicTimerListView(generics.ListAPIView):
    """
    API view to retrieve list of timers for public use, i.e., overlays for OBS.
    """
    serializer_class = TimerSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Timer.objects.filter(run__id = self.kwargs['run_id']).order_by('id')


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


class CreatePollSessionAPIView(generics.ListCreateAPIView):
    """
    API view to get list of poll sessions or create a new session.
    """
    serializer_class = CreatePollSessionSerializer
    permission_classes = [AllowAny]


    def create(self, request, *args, **kwargs):
        session_id = str(uuid.uuid4().hex[:6])
        moderator_token = f'{session_id}-mod-{uuid.uuid4().hex[:6]}'
        viewer_token = f'{session_id}-viewer'
        overlay_token = f'{session_id}-overlay'

        session_data = {
            'session_id': session_id,
            'published_question_id': None
        }

        r.set(f'poll:session:{session_id}', json.dumps(session_data), ex=86400)
        r.set(f'poll:token_map:{moderator_token}', session_id, ex=86400)
        r.set(f'poll:token_map:{viewer_token}', session_id, ex=86400)
        r.set(f'poll:token_map:{overlay_token}', session_id, ex=86400)

        response_data = {
                'moderator_url': f'/polls/m/{moderator_token}',
                'viewer_url': f'/polls/v/{viewer_token}',
                'overlay_url': f'/polls/o/{overlay_token}',
                'session_id': session_id,
            }

        serializer = self.get_serializer(response_data)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PollQuestionsListView(generics.ListCreateAPIView):
    """
    API view to get list of questions in poll or
    create a new question and add to Poll.
    """
    serializer_class = PollQuestionSerializer
    permission_classes = [AllowAny]

    def get_session_id(self):
        token = self.kwargs.get('client_token')
        return r.get(f'poll:token_map:{token}')

    def get_queryset(self):
        session_id = self.get_session_id()
        if not session_id:
            return []

        question_ids = r.lrange(f'poll:session:{session_id}:questions', 0, -1)
        questions = []
        for qid in question_ids:
            q_raw = r.get(f'poll:question:{qid}')
            if q_raw:
                questions.append(json.loads(q_raw))
        return questions

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        session_id = self.get_session_id()
        client_token = self.kwargs.get('client_token')

        if not session_id:
            serializer = ErrorResponseSerializer({'error': 'Invalid token'})
            return Response(serializer.data, status=status.HTTP_404_NOT_FOUND)

        if not client_token or '-mod' not in client_token:
            serializer = ErrorResponseSerializer({'error': 'Only moderator can submit questions.'})
            return Response(serializer.data, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        question_id = f'q-{uuid.uuid4().hex[:6]}'
        votes = {answer: 0 for answer in validated_data['answers']}

        question_record = {
            'id': question_id,
            'question': validated_data['question'],
            'answers': validated_data['answers'],
            'votes': votes
        }

        r.set(f'poll:question:{question_id}', json.dumps(question_record), ex=86400)
        r.rpush(f'poll:session:{session_id}:questions', question_id)

        out_serializer = self.get_serializer(question_record)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)


class DeletePollQuestionView(generics.DestroyAPIView):
    serializer_class = PollQuestionSerializer
    permission_classes = [AllowAny]

    def destroy(self, request, *args, **kwargs):
        moderator_token = kwargs['client_token']
        question_id = kwargs['question_id']
        session_id = r.get(f'poll:token_map:{moderator_token}')

        if not session_id:
            serializer = ErrorResponseSerializer({'error': 'Invalid token'})
            return Response(serializer.data, status=status.HTTP_404_NOT_FOUND)

        r.lrem(f'poll:session:{session_id}:questions', 0, question_id)
        r.delete(f'poll:question:{question_id}')

        serializer = SuccessResponseSerializer({'detail': 'Question deleted'})
        return Response(serializer.data, status=status.HTTP_200_OK)



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


class ModeratorPollsView(TemplateView):
    """
    View responsible for displaying dashboard for creating polls.
    """
    template_name = 'polls/polls_moderator.html'


class CreatePollSessionView(TemplateView):
    """
    View responsible for displaying dashboard for creating a new poll.
    """
    template_name = 'polls/create_poll_session.html'


class OverlayPollView(TemplateView):
    """
    View responsible for displaying an overlay of a poll for OBS streaming.
    """
    template_name = 'polls/overlay_poll.html'


class ViewerPollView(TemplateView):
    """
    View responsible for displaying list of questions for viewers to vote.
    """
    template_name = 'polls/viewer_poll.html'