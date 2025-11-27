from django.contrib import admin
from .models import Task, UserPreferences

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'due_date', 'importance', 'estimated_hours', 'priority_score', 'is_completed']
    list_filter = ['is_completed', 'importance']
    search_fields = ['title']

@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'urgency_weight', 'importance_weight', 'effort_weight', 'dependency_weight']
    
    def get_readonly_fields(self, request, obj=None):
        # Make weights editable but show validation
        return []