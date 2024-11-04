from django.contrib.auth.models import User
from django.db import models

class Question(models.Model):
    text = models.TextField()
    def _str_(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def _str_(self):
        return self.text

class UserScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f'{self.user.username} - {self.score}'