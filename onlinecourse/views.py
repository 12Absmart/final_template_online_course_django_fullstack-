from django.shortcuts import render
from django.http import HttpResponseRedirect
# <HINT> Import any new Models here
from .models import Course, Enrollment, Submission, Choice
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled



def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_answers.append(choice_id)
    return submitted_answers



def submit(request, course_id):
    # Get the current user
    user = request.user

    # Get the course object
    course = get_object_or_404(Course, id=course_id)

    # Get the associated enrollment for the current user and course
    enrollment = get_object_or_404(Enrollment, user=user, course=course)
    if request.method == 'POST':
        # Create a new submission object
        submission = Submission.objects.create(enrollment=enrollment)

        # Assuming your form data provides a list of selected choice IDs
        selected_choice_ids = request.POST.getlist('selected_choices')

        # Loop through the selected choice IDs and add them to the submission
        for choice_id in selected_choice_ids:
            choice = get_object_or_404(Choice, id=choice_id)
            submission.choices.add(choice)

        # Redirect to show_exam_result view with the submission id
        return redirect('show_exam_result', submission_id=submission.id)

    # Render a form to select choices
    # You'll need to create a template for this form
    return render(request, 'exam_result_bootstrap.html', {'course': course})



def show_exam_result(request, course_id, submission_id):
    # Get the course and submission objects based on their ids
    course = get_object_or_404(Course, id=course_id)
    submission = get_object_or_404(Submission, id=submission_id)

    # Get the selected choice ids from the submission
    selected_choice_ids = submission.choices.values_list('id', flat=True)

    # Initialize variables to track results
    total_score = 0
    question_results = []
     # Loop through questions in the course
    for question in course.questions.all():
        correct_choices = question.choices.filter(is_correct=True)

        # Check if all correct choices were selected
        is_correct = set(correct_choices.values_list('id', flat=True)) == set(selected_choice_ids)

        # Calculate the score for the question
        question_score = question.grade_point if is_correct else 0

        # Update total score
        total_score += question_score

        # Append question result to the list
        question_results.append({
            'question': question,
            'is_correct': is_correct,
            'question_score': question_score,
        })
         # Determine if the learner passed the exam
    passed_exam = total_score >= course.passing_score

    return render(request, 'exam_result_bootstrap.html', {
        'course': course,
        'submission': submission,
        'question_results': question_results,
        'total_score': total_score,
        'passed_exam': passed_exam,
    })




# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))



