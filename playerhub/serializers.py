from rest_framework import serializers
from .models import Run, WipeCounter, Timer, Game

class RunSerializer(serializers.ModelSerializer):
    """
    Serializer for the Run model.
    Handles the serialization and deserialization of Run instances.
    """
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    game = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all())
    game_name = serializers.ReadOnlyField(source='game.name', read_only=True)
    class Meta:
        model = Run
        fields = '__all__'

class WipeCounterSerializer(serializers.ModelSerializer):
    """
    Serializer for the WipeCounter model.
    Used to serialize and deserialize death counter data per game segment.
    """
    run = serializers.SlugRelatedField(slug_field='name', read_only=True)
    class Meta:
        model = WipeCounter
        fields = '__all__'

class TimerSerializer(serializers.ModelSerializer):
    """
    Serializer for the Timer model.
    Used to handle the elapsed time tracking of game segments.
    """
    run = serializers.SlugRelatedField(slug_field='name', read_only=True)
    class Meta:
        model = Timer
        fields = '__all__'

class GameSerializer(serializers.ModelSerializer):
    """
    Serializer for the Game model.
    Used to handle the creation and retrieval of game instances.
    """
    class Meta:
        model = Game
        fields = '__all__'
