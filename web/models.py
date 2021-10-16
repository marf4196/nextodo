from typing import Text
from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import SlugField
import datetime

class Task(models.Model):
    STATUSE =  (
        ('Active', 'Active'),
        ('Pending', 'Pending'),
        ('Fail', 'Fail'),
        ('Done', 'Done'),
        ('Canceled', 'Canceled'),
    )
    PRIORITY = (
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5'),
    )

    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    text        = models.CharField(max_length=512)
    priority    = models.CharField(default=1, max_length=1, choices=PRIORITY)
    statuse     = models.CharField(max_length=20, default='Pending', choices=STATUSE)
    due_date    = models.DateField('due date', blank=True, null=True)
    action_date = models.DateField('action date', blank=True, null=True, default='')
    create_date = models.DateField('create date', blank=True, null=True, default=datetime.datetime.now)

    def get_url(self):
        return f'/tasks/{self.id}'

    def get_edit_url(self):
        return f'/tasks/edit/{self.id}'
    
    def get_delete_url(self):
        return f'/tasks/delete/{self.id}'

    def get_deleteConfirm_url(self):
        return f'/tasks/deleteConfirm/{self.id}'

    def __str__(self):
        return  self.text

class TempUser(models.Model):
    username    = models.CharField(max_length=512)
    email       = models.CharField(max_length=512)
    password    = models.CharField(max_length=512)
    code        = models.CharField(max_length=512)
    phone       = models.CharField(max_length=512)

class news(models.Model):
    title       = models.CharField(max_length=512)
    text        = models.CharField(max_length=1024)
    is_active   = models.BooleanField()