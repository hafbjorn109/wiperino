from rest_framework import serializers
from .models import Run, WipeCounter, Timer, Game, MODE_CHOICES


class RunSerializer(serializers.ModelSerializer):
    """
    Serializer for the Run model.
    Handles the serialization and deserialization of Run instances.
    """
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    game = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all(), required=True)
    game_name = serializers.ReadOnlyField(source='game.name', read_only=True)
    mode = serializers.ChoiceField(choices=MODE_CHOICES, required=True)
    is_finished = serializers.BooleanField(default=False)

    class Meta:
        model = Run
        fields = [
            'id',
            'name',
            'game',
            'game_name',
            'mode',
            'user',
            'is_finished',
        ]
        read_only_fields = ['id', 'user', 'game_name']

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        if len(value) > 50:
            raise serializers.ValidationError("Name must be less than 50 characters.")
        return value


class WipeCounterSerializer(serializers.ModelSerializer):
    """
    Serializer for the WipeCounter model.
    Used to serialize and deserialize death counter data per game segment.
    """
    run = serializers.SlugRelatedField(slug_field='name', read_only=True)
    segment_name = serializers.CharField(max_length=50, required=True)
    count = serializers.IntegerField(min_value=0, default=0)
    is_finished = serializers.BooleanField(default=False)

    class Meta:
        model = WipeCounter
        fields = [
            'id',
            'run',
            'segment_name',
            'count',
            'is_finished',
        ]
        read_only_fields = ['id', 'run']

    def validate_segment_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Segment name cannot be empty.")
        return value

class TimerSerializer(serializers.ModelSerializer):
    """
    Serializer for the Timer model.
    Used to handle the elapsed time tracking of game segments.
    """
    run = serializers.SlugRelatedField(slug_field='name', read_only=True)
    segment_name = serializers.CharField(max_length=50, required=True)
    elapsed_time = serializers.FloatField(required=False, allow_null=True, min_value=0.0)
    is_finished = serializers.BooleanField(default=False)

    class Meta:
        model = Timer
        fields = [
            'id',
            'run',
            'segment_name',
            'elapsed_time',
            'is_finished',
        ]
        read_only_fields = ['id', 'run']

        def validate_segment_name(self, value):
            if not value.strip():
                raise serializers.ValidationError("Segment name cannot be empty.")
            return value


class GameSerializer(serializers.ModelSerializer):
    """
    Serializer for the Game model.
    Used to handle the creation and retrieval of game instances.
    """
    name = serializers.CharField(max_length=50, required=True)

    class Meta:
        model = Game
        fields = ['id', 'name']
        read_only_fields = ['id']

        def validate_name(self, value):
            if not value.strip():
                raise serializers.ValidationError("Name cannot be empty.")
            if Game.objects.filter(name__iexact=value).exists():
                raise serializers.ValidationError("Game with this name already exists.")
            return value


class CreatePollSessionSerializer(serializers.Serializer):
    """
    Serializer for creating a new poll session.
    """
    session_id = serializers.CharField(read_only=True)
    moderator_url = serializers.CharField(read_only=True)
    viewer_url = serializers.CharField(read_only=True)
    overlay_url = serializers.CharField(read_only=True)


class PollQuestionSerializer(serializers.Serializer):
    """
    Serializer for creating a new poll question.
    """
    id = serializers.CharField(read_only=True)
    question = serializers.CharField(max_length=300)
    answers = serializers.ListField(
        child=serializers.CharField(max_length=100),
        min_length=2,
    )
    votes = serializers.DictField(
        child=serializers.IntegerField(), required=False, read_only=False
    )

    def validate_question(self, value):
        if not value.strip():
            raise serializers.ValidationError("Question cannot be empty.")
        return value

    def validate_answers(self, value):
        cleaned = [ans.strip() for ans in value]
        if len(cleaned) < 2:
            raise serializers.ValidationError("Question must have at least 2 answers.")
        if len(set(cleaned)) != len(cleaned):
            raise serializers.ValidationError("Question cannot have duplicate answers.")
        return cleaned


class PollVoteSerializer(serializers.Serializer):
    """
    Serializer for creating a new poll vote.
    """
    question_id = serializers.CharField(max_length=100)
    answer = serializers.CharField(max_length=100)

    def validate_question_id(self, value):
        if not value.strip():
            raise serializers.ValidationError("Question ID cannot be empty.")
        return value

    def validate_answer(self, value):
        if not value.strip():
            raise serializers.ValidationError("Answer cannot be empty.")
        return value


class ErrorResponseSerializer(serializers.Serializer):
    """
    Serializer for creating a new error response.
    """
    error = serializers.CharField()


class SuccessResponseSerializer(serializers.Serializer):
    """
    Serializer for creating a new success response.
    """
    detail = serializers.CharField()


class PublishedQuestionSerializer(serializers.Serializer):
    """
    Serializer for publishing a poll question to all connected clients.
    Used in WebSocket communication between moderator and viewers/overlay.
    """
    type = serializers.ChoiceField(choices=['publish_question'])
    question_id = serializers.CharField(max_length=100)
    question_data = PollQuestionSerializer()

    def validate_question_id(self, value):
        if not value.strip():
            raise serializers.ValidationError("Question ID cannot be empty.")
        return value


class WebSocketErrorSerializer(serializers.Serializer):
    """
    Serializer for publishing a poll question to all connected clients.
    Used in WebSocket communication between moderator and viewers/overlay.
    """
    type = serializers.ChoiceField(choices=['error'])
    error = serializers.CharField()


class VoteUpdateSerializer(serializers.Serializer):
    """
    Serializer for sending live vote updates to connected WebSocket clients.
    Includes question ID, answer options and current vote counts.
    """
    type = serializers.ChoiceField(choices=['vote'])
    question_id = serializers.CharField(max_length=100)
    answers = serializers.ListField(child=serializers.CharField(max_length=100))
    votes = serializers.DictField(child=serializers.IntegerField(min_value=0))

    def validate_question_id(self, value):
        if not value.strip():
            raise serializers.ValidationError("Question ID cannot be empty.")
        return value

    def validate_answers(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Question must have at least 2 answers.")
        if len(set(value)) != len(value):
            raise serializers.ValidationError("Question cannot have duplicate answers.")
        return value

    def validate(self, data):
        missing = [key for key in data['votes'].keys() if key not in data['answers']]
        if missing:
            raise serializers.ValidationError(f"Missing votes for answers: {missing}")
        return data


class NewQuestionSerializer(serializers.Serializer):
    """
    Serializer for sending a newly created question to all WebSocket clients.
    Used when syncing question list or broadcasting a new question.
    """
    type = serializers.ChoiceField(choices=['new_question'])
    question = PollQuestionSerializer()


class DeleteQuestionSerializer(serializers.Serializer):
    """
    Serializer for instructing WebSocket clients to delete a specific question.
    Typically triggered by a moderator.
    """
    type = serializers.ChoiceField(choices=['delete_question'])
    question_id = serializers.CharField(max_length=100)

    def validate_question_id(self, value):
        if not value.strip():
            raise serializers.ValidationError("Question ID cannot be empty.")
        return value


class UnpublishQuestionSerializer(serializers.Serializer):
    """
    Serializer for unpublishing a currently visible question.
    Informs all WebSocket clients to hide the current question from view.
    """
    type = serializers.ChoiceField(choices=['unpublish_question'])


class WipeUpdateSerializer(serializers.Serializer):
    """
    Input serializer for updating the wipe count of a segment.
    Used when the user increments or decrements the counter.
    """
    segment_id = serializers.IntegerField(min_value=1)
    count = serializers.IntegerField(min_value=0)


class NewSegmentSerializer(serializers.Serializer):
    """
    Input serializer for creating a new segment in a run.
    Includes initial count and finished status.
    """
    segment_id = serializers.IntegerField(min_value=1)
    segment_name = serializers.CharField(max_length=50)
    count = serializers.IntegerField(min_value=0)
    is_finished = serializers.BooleanField(default=False)

    def validate_segment_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Segment name cannot be empty.")
        return value


class SegmentFinishedSerializer(serializers.Serializer):
    """
    Input serializer for marking a segment as finished.
    """
    segment_id = serializers.IntegerField(min_value=1)


class RunFinishedSerializer(serializers.Serializer):
    """
    Input serializer for marking the entire run as finished.
    """
    type = serializers.ChoiceField(choices=['run_finished'])


class WipeUpdateBroadcastSerializer(serializers.Serializer):
    """
    Output serializer for broadcasting a wipe counter update
    to all connected clients in a run group.
    """
    type = serializers.ChoiceField(choices=['wipe_update'])
    segment_id = serializers.IntegerField(min_value=1)
    count = serializers.IntegerField(min_value=0)
    user = serializers.CharField()


class NewSegmentBroadcastSerializer(serializers.Serializer):
    """
    Output serializer for broadcasting a newly created segment
    to all connected clients in a run group.
    """
    type = serializers.ChoiceField(choices=['new_segment'])
    segment_id = serializers.IntegerField(min_value=1)
    segment_name = serializers.CharField(max_length=50)
    count = serializers.IntegerField(min_value=0)
    is_finished = serializers.BooleanField(default=False)
    user = serializers.CharField()

    def validate_segment_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Segment name cannot be empty.")
        return value


class SegmentFinishedBroadcastSerializer(serializers.Serializer):
    """
    Output serializer for broadcasting the information
    that a segment has been marked as finished.
    """
    type = serializers.ChoiceField(choices=['segment_finished'])
    segment_id = serializers.IntegerField(min_value=1)
    user = serializers.CharField()


class RunFinishedBroadcastSerializer(serializers.Serializer):
    """
    Output serializer for broadcasting that a run has been completed.
    """
    type = serializers.ChoiceField(choices=['run_finished'])
    user = serializers.CharField()


class TimerBaseSerializer(serializers.Serializer):
    """
    Base serializer used for all timer-related WebSocket messages.
    """
    segment_id = serializers.IntegerField(min_value=1)
    elapsed_time = serializers.FloatField(min_value=0.0)


class TimerStartSerializer(TimerBaseSerializer):
    """
    Input serializer for starting a timer on a given segment.
    Requires the current elapsed_time and timestamp.
    """
    type = serializers.ChoiceField(choices=['start_timer'])
    started_at = serializers.DateTimeField()


class TimerPauseSerializer(TimerBaseSerializer):
    """
    Input serializer for pausing a timer.
    Expects the current total elapsed_time.
    """
    type = serializers.ChoiceField(choices=['pause_timer'])


class TimerFinishSerializer(TimerBaseSerializer):
    """
    Input serializer for finishing a timer.
    Sets the segment as finished and passes final elapsed_time.
    """
    type = serializers.ChoiceField(choices=['finish_timer'])


class TimerBroadcastSerializer(serializers.Serializer):
    """
    Output serializer for broadcasting any timer-related event,
    including start, pause, update, and finish.
    """
    type = serializers.ChoiceField(choices=
                                   ['start_timer', 'timer_update', 'finish_timer', 'pause_timer', 'run_finished'])
    segment_id = serializers.IntegerField(min_value=1, required=False)
    elapsed_time = serializers.FloatField(min_value=0.0, required=False)
    user = serializers.CharField()
    started_at = serializers.DateTimeField(required=False, allow_null=True)
    is_finished = serializers.BooleanField(default=False)


class NewTimerSegmentSerializer(serializers.Serializer):
    """
    Input serializer for broadcasting newly created timer segment to clients.
    """
    type = serializers.ChoiceField(choices=['new_segment'])
    segment_id = serializers.IntegerField(min_value=1)
    segment_name = serializers.CharField(max_length=50)
    elapsed_time = serializers.FloatField(min_value=0.0)
    is_finished = serializers.BooleanField(default=False)
    user = serializers.CharField(required=False)

    def validate_segment_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Segment name cannot be empty.")
        return value