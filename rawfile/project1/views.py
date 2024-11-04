from django.core.mail import send_mail
from django.db.models import Avg, Max, Min
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
from .models import Question, Answer, UserScore
import random

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.email = form.cleaned_data.get('email')
            user.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'project1/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Invalid username or password.')
                print(f"Login failed for username: {username}")
    else:
        form = LoginForm()
    return render(request, 'project1/login.html', {'form': form})

def user_logout(request):
    logout(request)
    print("User logged out")
    return redirect('login')

@login_required
def home(request):
    print("Home page accessed")
    return render(request, 'project1/home.html')

@login_required
def quiz(request):
    print("Quiz view accessed")
    questions = list(Question.objects.all())
    random.shuffle(questions)

    if len(questions) < 7:
        return render(request, 'project1/quiz_results.html', {'score': 0, 'message': 'Not enough questions available.'})

    questions = questions[:7]

    if 'question_index' not in request.session:
        request.session['question_index'] = 0
        request.session['questions'] = [q.id for q in questions]
        request.session['user_answers'] = {}
        request.session['score'] = 0

    question_index = request.session['question_index']
    question_ids = request.session['questions']

    if question_index >= len(question_ids):
        request.session['question_index'] = 0
        question_index = 0

    if request.method == 'POST':
        selected_answer_id = request.POST.get('answer')
        if selected_answer_id:
            question_id = question_ids[question_index]
            selected_answer = get_object_or_404(Answer, id=selected_answer_id)
            if selected_answer.is_correct:
                request.session['score'] += 1
                print(f"Correct answer selected for question ID: {question_id}")
            request.session['user_answers'][str(question_id)] = selected_answer_id

        request.session['question_index'] += 1
        if request.session['question_index'] >= len(question_ids):
            return redirect('quiz_results')
        else:
            return redirect('quiz')

    question_id = question_ids[question_index]
    question = get_object_or_404(Question, id=question_id)

    question_number = question_index + 1

    context = {
        'question': question,
        'question_index': question_index,
        'question_number': question_number,
        'total_questions': len(question_ids)
    }
    return render(request, 'project1/question.html', context)

@login_required
def quiz_results(request):
    print("Quiz results view accessed")
    score = request.session.get('score', 0)
    UserScore.objects.create(user=request.user, score=score)

    average_score = UserScore.objects.aggregate(Avg('score'))['score__avg']
    highest_score = UserScore.objects.aggregate(Max('score'))['score__max']
    lowest_score = UserScore.objects.aggregate(Min('score'))['score__min']

    total_questions = 7
    passing_score = total_questions / 2
    show_retakes = score < passing_score

    past_scores = UserScore.objects.filter(user=request.user).order_by('-date_taken')

    context = {
        'score': score,
        'average_score': average_score,
        'highest_score': highest_score,
        'lowest_score': lowest_score,
        'show_retakes': show_retakes,
        'past_scores': past_scores
    }

    subject = 'Quiz Completed!'
    message = f'Hi {request.user.username},\n\nYou have completed the quiz.\nYour score: {score}\n\nThank you for participating!'
    from_email = 'thelambtonprofessionals@gmail.com'
    recipient_list = [request.user.email]

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )
    print(f"Email sent to {request.user.email} with score {score}")

    request.session.pop('questions', None)
    request.session.pop('question_index', None)
    request.session.pop('score', None)

    return render(request, 'project1/quiz_results.html', context)

@login_required
def practice_quiz(request):
    print("Practice quiz view accessed")
    questions = list(Question.objects.all())
    if len(questions) < 7:
        return render(request, 'project1/practice_quiz_results.html', {'score': 0, 'message': 'Not enough questions available.'})

    random.shuffle(questions)
    questions = questions[:7]
    if 'practice_question_index' not in request.session:
        request.session['practice_question_index'] = 0
        request.session['practice_questions'] = [q.id for q in questions]
        request.session['practice_answers'] = {}
    practice_question_index = request.session.get('practice_question_index', 0)
    practice_question_ids = request.session.get('practice_questions', [])
    if not practice_question_ids:
        request.session['practice_questions'] = [q.id for q in questions]
        practice_question_ids = request.session['practice_questions']
    if 'practice_answers' not in request.session:
        request.session['practice_answers'] = {}
    if request.method == 'POST':
        selected_answer_id = request.POST.get('answer')
        if selected_answer_id:
            question_id = practice_question_ids[practice_question_index]
            request.session['practice_answers'][str(question_id)] = selected_answer_id
        request.session['practice_question_index'] += 1
        if request.session['practice_question_index'] >= len(practice_question_ids):
            score = 0
            for question_id, selected_answer_id in request.session['practice_answers'].items():
                question = get_object_or_404(Question, id=question_id)
                correct_answer = question.answers.filter(is_correct=True).first()
                if correct_answer and str(correct_answer.id) == selected_answer_id:
                    score += 1
            request.session.pop('practice_question_index', None)
            request.session.pop('practice_questions', None)
            request.session.pop('practice_answers', None)
            print(f"Practice quiz completed with score: {score}")
            return render(request, 'project1/practice_quiz_results.html', {'score': score})
        else:
            return redirect('practice_quiz')
    if practice_question_index >= len(practice_question_ids):
        request.session['practice_question_index'] = 0
        request.session.pop('practice_questions', None)
        request.session.pop('practice_answers', None)
        print("No more practice questions available")
        return render(request, 'project1/practice_quiz_results.html', {'score': 0, 'message': 'No more questions available.'})
    question_id = practice_question_ids[practice_question_index]
    question = get_object_or_404(Question, id=question_id)
    question_number = practice_question_index + 1
    context = {
        'question': question,
        'question_index': practice_question_index,
        'question_number': question_number
    }
    return render(request, 'project1/practice_quiz.html', context)

@login_required
def review_quiz(request):
    user_answers = request.session.get('user_answers', {})
    if not user_answers:
        return render(request, 'project1/review_quiz.html', {'message': 'No data available.'})
    question_ids = list(user_answers.keys())
    questions = Question.objects.filter(id__in=question_ids)
    review_data = []
    for question in questions:
        selected_answer_id = user_answers.get(str(question.id))
        selected_answer = question.answers.filter(id=selected_answer_id).first() if selected_answer_id else None
        correct_answer = question.answers.filter(is_correct=True).first()
        review_data.append({
            'question': question,
            'selected_answer': selected_answer,
            'correct_answer': correct_answer
        })
    context = {
        'review_data': review_data
    }
    request.session.pop('user_answers', None)
    return render(request, 'project1/review_quiz.html', context)