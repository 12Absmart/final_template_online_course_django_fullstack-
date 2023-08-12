"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from onlinecourse.views import CourseListView, CourseDetailView, registration_request, login_request, show_exam_result, submit, enroll

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', CourseListView.as_view(), name='home'),  # Redirect to CourseListView when root URL is accessed
    path('registration/', registration_request, name='registration'),
    path('login/', login_request, name='login'),
    path('courses/', CourseListView.as_view(), name='courses'),
    path('course/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('submit/<int:course_id>/',submit, name='submit'),
    path('enroll/<int:course_id>/', enroll, name='enroll'),
    path('show_exam_result/<int:course_id>/<int:submission_id>/', show_exam_result, name='show_exam_result'),
    path('onlinecourse/', include('onlinecourse.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)