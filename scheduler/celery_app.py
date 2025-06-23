from celery import Celery
import os
from dotenv import load_dotenv
from celery.schedules import crontab

# Load environment variables
load_dotenv()

# Initialize Celery
app = Celery('scheduler')

# Load tasks module
app.conf.imports = ['scheduler.tasks']
app.conf.timezone = 'Asia/Kolkata'
# Celery configuration

app.conf.broker_url = os.getenv("CELERY_BROKER_URL")
app.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND")
app.conf.timezone = 'UTC'
app.conf.enable_utc = True

# Add periodic tasks

app.conf.beat_schedule = {
    'process-wordpress-posts': {
        'task': 'scheduler.tasks.process_wordpress_posts',
        'schedule': crontab(minute=0, hour=9),  # Runs daily at 9 AM,  # Runs daily at 9 AM
    },
}
# app.conf.beat_schedule = {
#     'process-wordpress-posts': {
#         'task': 'scheduler.tasks.process_wordpress_posts',
#         'schedule': crontab(hour=9, minute=0),  # Run at 9:00 AM every day
#     },
# }

if __name__ == '__main__':
    app.start()