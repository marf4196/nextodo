from django.contrib import admin
from .models import Task, TempUser

admin.site.register(Task)
admin.site.register(TempUser)