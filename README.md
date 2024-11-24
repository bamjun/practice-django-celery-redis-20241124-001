# 장고 셀러리 빗트 사용하기

## 1. 프로젝트 생성

1. Poetry를 사용하여 새 프로젝트 생성:
```bash
poetry init
```

2. 필요한 패키지 설치:
```bash
poetry add django celery redis django-celery-beat
```

```bash
poetry add django "celery[redis]" django-celery-beat
```

3. Django 프로젝트 생성:
```bash
django-admin startproject core .
python manage.py startapp myapp
```

## 2. 레디스 설치

1. Redis 설치 (메시지 브로커로 사용):
- Mac OS:
```bash
brew install redis
brew services start redis
```
- Ubuntu:
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

2. Redis 서버 실행 확인:
```bash
redis-cli ping
```
응답으로 "PONG"이 나오면 정상 작동

## 3. 셀러리 설정

1. Celery 설정 파일 생성 (`core/celery.py`):
```python
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

2. Django 설정 파일에 Celery 설정 추가 (`core/settings.py`):
```python
INSTALLED_APPS = [
    ...
    'django_celery_beat',
    'myapp',
]

# Celery 설정
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Seoul'

# Celery Beat 설정
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
```

3. 태스크 생성 (`myapp/tasks.py`):
```python
from celery import shared_task
from datetime import datetime

@shared_task
def my_scheduled_task():
    now = datetime.now()
    print(f"My scheduled task is running at {now}")
    return f"Task completed at {now}"
```

4. init 파일 생성 (`core/__init__.py`):
```python
from __future__ import absolute_import, unicode_literals

# Celery 앱을 가져옵니다
from .celery import app as celery_app

# Celery 앱을 프로젝트 내에서 사용할 수 있도록 노출
__all__ = ['celery_app']
```


## 4. 실행 방법

1. Django 서버 실행:
```bash
python manage.py runserver
```

2. Celery Worker 실행:
```bash
celery -A core worker -l info
```

3. Celery Beat 실행:
```bash
celery -A core beat -l info
```

4. 데이터베이스 스케줄러 사용(옵션):
```bash
celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## 5. 스케줄 작업 관리

1. Django 관리자 페이지에서 주기적 작업 설정:
- http://localhost:8000/admin 접속
- Periodic Tasks 섹션에서 새로운 주기적 작업 추가
- Interval 또는 Crontab 스케줄 설정
- 실행할 태스크 선택

2. 프로그래매틱하게 스케줄 설정:
```python
from django_celery_beat.models import PeriodicTask, IntervalSchedule

# 30초마다 실행되는 스케줄 생성
schedule = IntervalSchedule.objects.create(
    every=30,
    period=IntervalSchedule.SECONDS,
)

# 주기적 작업 생성
PeriodicTask.objects.create(
    name='My Task',
    task='myapp.tasks.my_scheduled_task',
    interval=schedule,
    enabled=True
)
```

## 6. 주의사항

1. Redis 서버가 실행 중인지 확인
2. Celery Worker와 Beat가 모두 실행 중인지 확인
3. 시간대 설정이 올바른지 확인
4. 데이터베이스 마이그레이션 실행 필요:
```bash
python manage.py migrate
```

## 7. 문제해결

1. Redis 연결 오류:
- Redis 서버 실행 상태 확인
- CELERY_BROKER_URL 설정 확인

2. 태스크가 실행되지 않을 때:
- Celery Worker 로그 확인
- 태스크 등록 여부 확인
- 태스크 이름이 올바른지 확인

3. Beat 스케줄이 작동하지 않을 때:
- Beat 프로세스 실행 여부 확인
- 관리자 페이지에서 스케줄 활성화 상태 확인







---
---
---
---

# 동시성제어
동일한 태스크가 100개 있더라도 Celery는 자동으로 멈추지 않습니다. 하지만 이는 시스템 리소스에 부담을 줄 수 있으므로, 다음과 같은 방법들로 관리하는 것이 좋습니다:

1. **동시성 제어**
태스크에 `acks_late`와 `unique` 옵션을 사용하여 중복 실행을 방지할 수 있습니다:

````python:django/myapp/tasks.py
from celery import shared_task
from datetime import datetime
from celery.utils.log import get_task_logger
from django.core.cache import cache

logger = get_task_logger(__name__)

@shared_task(
    acks_late=True,
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def my_scheduled_task(self):
    # 락 키 생성
    lock_id = f"lock_my_scheduled_task"
    
    # 이미 실행 중인지 확인
    if cache.get(lock_id):
        logger.info("Task already running")
        return "Task already running"
    
    try:
        # 락 설정 (60초 동안 유효)
        cache.set(lock_id, True, 60)
        
        now = datetime.now()
        logger.info(f"Task running at {now}")
        return f"Task completed at {now}"
        
    finally:
        # 작업 완료 후 락 해제
        cache.delete(lock_id)
````

2. **작업 큐 설정**
`settings.py`에 Celery 설정을 추가하여 동시 실행 수를 제한할 수 있습니다:

````python:django/core/settings.py
# ... 기존 설정들 ...

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# 작업자 설정
CELERY_WORKER_CONCURRENCY = 4  # 동시 실행 워커 수
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # 워커당 가져올 작업 수
CELERY_WORKER_MAX_TASKS_PER_CHILD = 100  # 워커당 최대 작업 수
````

3. **Rate Limiting 설정**
태스크에 rate limit을 설정하여 초당/분당 실행 횟수를 제한할 수 있습니다:

````python:django/myapp/tasks.py
@shared_task(rate_limit='10/m')  # 분당 10회로 제한
def my_scheduled_task():
    # ... 태스크 코드 ...
````

4. **모니터링 추가**
태스크 실행 상태를 모니터링하기 위한 로깅을 추가하는 것이 좋습니다:

````python:django/myapp/tasks.py
@shared_task
def my_scheduled_task():
    logger = get_task_logger(__name__)
    
    try:
        now = datetime.now()
        logger.info(f"Starting task at {now}")
        
        # 작업 수행
        result = f"Task completed at {now}"
        
        logger.info(result)
        return result
        
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        raise
````

5. **에러 처리와 재시도 로직**
실패한 태스크에 대한 재시도 로직을 추가할 수 있습니다:

````python:django/myapp/tasks.py
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def my_scheduled_task(self):
    try:
        now = datetime.now()
        # ... 작업 수행 ...
        return f"Task completed at {now}"
    except Exception as exc:
        logger.error(f"Task failed: {str(exc)}")
        self.retry(exc=exc)
````

이러한 방법들을 통해 많은 수의 동일한 태스크가 있더라도 시스템을 안정적으로 운영할 수 있습니다. 실제 운영 환경에서는 시스템의 리소스 상황과 요구사항에 맞게 위의 설정들을 조정하시면 됩니다.