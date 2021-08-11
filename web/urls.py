from django.contrib import admin
from django.urls import path
from .views import *
app_name = 'web'
urlpatterns = [
    path('', index_view, name='index'),

    path('register/',   register_view, name='register'),
    path('login/',      login_view, name='login'),
    path('logout/',     logout_view, name='logout'),
    path('active/', active_view, name='active' ),

    path('tasks/', tasks_view, name='tasks'),
    path('tasks/add/',    taskAdd_view, name='taskAd'),
    path('tasks/<int:id>/', taskShow_view, name='taskShow'),
    path('tasks/edit/<int:id>', taskEdit_view, name='taskEdit'),
    path('tasks/delete/<int:id>', taskDelete_view, name='taskDelete'),
    path('tasks/deleteConfirm/<int:id>', taskDeleteConfirm_view, name='taskDeleteConfirm'),
]