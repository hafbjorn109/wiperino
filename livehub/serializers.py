from rest_framework import serializers
from .models import Poll, Answer


class PollSerializer(serializers.ModelSerializer):
    """
    Serializer for the Poll model.
    Handles creation and retrieval of poll instances.
    """
    run = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Poll
        fields = '__all__'


class AnswerSerializer(serializers.ModelSerializer):
    """
    Serializer for the Answer model.
    Manages serialization of poll answers and vote counts.
    """
    poll = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Answer
        fields = '__all__'
