from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'due_date', 'importance', 'estimated_hours', 'priority_score', 'is_completed']
    list_filter = ['is_completed', 'importance']
    search_fields = ['title']