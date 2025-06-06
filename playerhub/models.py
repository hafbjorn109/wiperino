from django.db import models
from django.contrib.auth.models import User

MODE_CHOICES = [
    ('SPEEDRUN', 'Speedrun'),
    ('WIPECOUNTER', 'Wipe Counter'),
]


class Game(models.Model):
    """
    Represents a single game available for choose for a session to create.
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Run(models.Model):
    """
    Represents a game session created by a user.
    Can operate in two modes: speedrun timer or wipe counter.
    """
    name = models.CharField(max_length=50)
    game = models.ForeignKey(Game, on_delete=models.PROTECT)
    mode = models.CharField(choices=MODE_CHOICES, max_length=30)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    youtube_link = models.URLField(null=True, blank=True)

    def __str__(self):
        return f'{self.name} | {self.game} | {self.mode}'


class WipeCounter(models.Model):
    """
    Represents the death counter for a specific segment of a game session.
    Each segment is linked to a particular Run instance.
    """
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    segment_name = models.CharField(max_length=50)
    count = models.IntegerField(default=0)
    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.run.name} | {self.segment_name}'


class Timer(models.Model):
    """
    Represents the elapsed time tracking for a specific segment of a game session.
    Stores the final elapsed time value sent by the client.
    """
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    segment_name = models.CharField(max_length=50)
    elapsed_time = models.FloatField(null=True, blank=True)
    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.run.name} | {self.segment_name}'
