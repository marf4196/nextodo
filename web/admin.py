from django.contrib import admin
from .models import Task, TempUser, news

admin.site.register(Task)
admin.site.register(TempUser)
admin.site.register(news)