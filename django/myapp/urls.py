from django.urls import path
from .views import run_task

urlpatterns = [
    path('run-task/', run_task, name='run-task'),
]
