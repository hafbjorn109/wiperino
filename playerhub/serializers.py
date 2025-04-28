from rest_framework import serializers
from .models import Run, WipeCounter, Timer

class RunSerializer(serializers.ModelSerializer):
    """
    Serializer for the Run model.
    Handles the serialization and deserialization of Run instances.
    """
    class Meta:
        model = Run
        fields = '__all__'

class WipeCounterSerializer(serializers.ModelSerializer):
    """
    Serializer for the WipeCounter model.
    Used to serialize and deserialize death counter data per game segment.
    """
    class Meta:
        model = WipeCounter
        fields = '__all__'

class TimerSerializer(serializers.ModelSerializer):
    """
    Serializer for the Timer model.
    Used to handle the elapsed time tracking of game segments.
    """
    class Meta:
        model = Timer
        fields = '__all__'