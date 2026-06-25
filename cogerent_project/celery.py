"""
Configuration Celery pour Co-Gérant
"""
import os
from celery import Celery

# Définir le module de settings Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cogerent_project.settings')

app = Celery('cogerent_project')

# Charger la configuration depuis Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-découvrir les tâches dans toutes les apps Django
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')