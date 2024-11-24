from django.http import JsonResponse
from .tasks import add, multiply, say_hello

def run_task(request):
    # 비동기 작업 호출
    task1 = add.delay(4, 6)
    task2 = multiply.delay(3, 7)
    task3 = say_hello.delay("Beomjune")

    return JsonResponse({
        'add_task_id': task1.id,
        'multiply_task_id': task2.id,
        'say_hello_task_id': task3.id,
    })
