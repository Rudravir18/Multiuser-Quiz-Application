from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('quiz/', views.quiz, name='quiz'),
    path('quiz/<int:question_index>/', views.quiz, name='quiz_with_index'),
    path('quiz_results/', views.quiz_results, name='quiz_results'),
    path('practice_quiz/', views.practice_quiz, name='practice_quiz'),
    path('review_quiz/', views.review_quiz, name='review_quiz'),
]
