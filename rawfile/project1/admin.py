from django.contrib import admin
from .models import Question, Answer, UserScore

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text',)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'is_correct')

@admin.register(UserScore)
class UserScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'date_taken')
