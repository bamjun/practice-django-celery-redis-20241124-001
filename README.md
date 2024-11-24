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

3. Django 프로젝트 생성:
```bash
django-admin startproject core .
python manage.py startapp myapp
```

## 2. 셀러리 설치

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
