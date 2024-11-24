from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Django의 settings.py를 기본 설정으로 지정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  # 'core'를 실제 프로젝트 이름으로 변경

app = Celery('core')

# Django의 설정을 Celery 설정으로 사용
app.config_from_object('django.conf:settings', namespace='CELERY')

# 자동으로 tasks.py에서 작업을 찾도록 설정
app.autodiscover_tasks()

# # 기본 beat 스케줄 설정 (선택사항)
# app.conf.beat_schedule = {
#     'test-every-30-seconds': {
#         'task': 'myapp.tasks.my_scheduled_task',
#         'schedule': 30.0,
#     },
# }
