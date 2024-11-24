from celery import shared_task
from datetime import datetime

@shared_task
def add(x, y):
    return x + y

@shared_task
def multiply(x, y):
    return x * y

@shared_task
def say_hello(name):
    return f"Hello, {name}!"

@shared_task(name='myapp.tasks.my_scheduled_task')
def my_scheduled_task():
    now = datetime.now()
    print(f"My scheduled task is running at {now}")
    return f"Task completed at {now}"
