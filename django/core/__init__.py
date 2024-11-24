from __future__ import absolute_import, unicode_literals

# Celery 앱을 가져옵니다
from .celery import app as celery_app

# Celery 앱을 프로젝트 내에서 사용할 수 있도록 노출
__all__ = ['celery_app']
