import logging
 
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from esports.celery import app
 
 
@app.task
def temp_task():
    print("Task executed! Horray...")
