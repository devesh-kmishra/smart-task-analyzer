from rest_framework import serializers
from .models import Task

def validate_dependencies(self, value):
    """Ensure dependencies exist"""
    if value:
        existing_ids = Task.objects.filter(id__in=value).values_list('id', flat=True)
        if len(existing_ids) != len(value):
            raise serializers.ValidationError("Some dependency IDs don't exist")
        
        # Check for circular dependencies (only on update)
        if self.instance:  # If updating existing task
            all_tasks = Task.objects.all()
            try:
                validate_dependencies(self.instance.id, value, all_tasks)
            except Exception as e:
                raise serializers.ValidationError(str(e))
            
    return value

class TaskSerializer(serializers.ModelSerializer):
    priority_score = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'due_date', 'estimated_hours',
            'importance', 'dependencies', 'is_completed',
            'priority_score', 'created_at', 'updated_at'
        ]

class TaskAnalysisSerializer(serializers.Serializer):
    """For analyze endpoint"""
    tasks = TaskSerializer(many=True)

class TaskSuggestionSerializer(serializers.Serializer):
    """For suggest endpoint"""
    task = TaskSerializer()
    reason = serializers.CharField()
    score = serializers.FloatField()