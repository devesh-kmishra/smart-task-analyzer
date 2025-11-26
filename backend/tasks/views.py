from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer, TaskSuggestionSerializer
from .scoring import TaskScorer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    
    @action(detail=False, methods=['post'])
    def analyze(self):
        """
        POST /api/tasks/analyze/
        Accepts list of tasks and returns them sorted by priority
        """
        # Get all tasks (or use tasks from request if provided)
        tasks = Task.objects.filter(is_completed=False)
        
        # Calculate scores
        scorer = TaskScorer()
        all_tasks_list = list(tasks)
        
        for task in all_tasks_list:
            task.priority_score = scorer.calculate_priority_score(task, all_tasks_list)
            task.save()
        
        # Sort by score
        sorted_tasks = sorted(all_tasks_list, key=lambda t: t.priority_score, reverse=True)
        
        serializer = TaskSerializer(sorted_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def suggest(self):
        """
        GET /api/tasks/suggest/
        Returns top 3 tasks to work on today with explanations
        """
        tasks = Task.objects.filter(is_completed=False)
        
        if not tasks.exists():
            return Response({"suggestions": []})
        
        # Calculate scores
        scorer = TaskScorer()
        all_tasks_list = list(tasks)
        
        task_scores = []
        for task in all_tasks_list:
            score = scorer.calculate_priority_score(task, all_tasks_list)
            reason = scorer.generate_suggestion_reason(task, all_tasks_list)
            task_scores.append({
                'task': task,
                'score': score,
                'reason': reason
            })
        
        # Sort and get top 3
        task_scores.sort(key=lambda x: x['score'], reverse=True)
        top_3 = task_scores[:3]
        
        serializer = TaskSuggestionSerializer(top_3, many=True)
        return Response({"suggestions": serializer.data})