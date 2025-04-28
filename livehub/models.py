from django.db import models
from playerhub.models import Run

# Create your models here.

class Poll(models.Model):
    """
    Represents a poll created during a game session.
    Allows viewers to answer questions during gameplay.
    """
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    published = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

class Answer(models.Model):
    """
    Represents a possible answer to a poll question.
    Stores the number of votes received for this particular answer.
    """
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    answer = models.CharField(max_length=50)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.answer