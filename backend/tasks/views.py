from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Task
from .serializers import TaskSerializer, TaskSuggestionSerializer
from .scoring import TaskScorer, has_circular_dependency

@method_decorator(csrf_exempt, name='dispatch')
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """
        POST /api/tasks/analyze/
        Accepts list of tasks and returns them sorted by priority
        Uses the Smart Balance strategy by default
        """
        # Get all incomplete tasks
        tasks = Task.objects.filter(is_completed=False)
        
        if not tasks.exists():
            return Response([])
        
        # Calculate scores using Smart Balance algorithm
        scorer = TaskScorer()
        all_tasks_list = list(tasks)
        
        for task in all_tasks_list:
            task.priority_score = scorer.calculate_priority_score(task, all_tasks_list)
            task.save()
        
        # Sort by score (highest first)
        sorted_tasks = sorted(all_tasks_list, key=lambda t: t.priority_score, reverse=True)
        
        serializer = TaskSerializer(sorted_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def suggest(self, request):
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
    
    @action(detail=False, methods=['get'])
    def dependency_graph(self, request):
        """GET /api/tasks/dependency_graph/"""
        tasks = Task.objects.all()
        
        # Build dependency map
        dep_map = {t.id: list(t.dependencies) for t in tasks}
        
        # Find circular dependencies
        circular_tasks = set()
        for task_id in dep_map.keys():
            if has_circular_dependency(task_id, dep_map):
                circular_tasks.add(task_id)
        
        # Build graph data
        nodes = []
        edges = []
        
        for task in tasks:
            nodes.append({
                'id': task.id,
                'title': task.title,
                'has_cycle': task.id in circular_tasks
            })
            
            for dep_id in task.dependencies:
                edges.append({
                    'from': dep_id,  # Dependency
                    'to': task.id,    # Task that depends on it
                    'has_cycle': task.id in circular_tasks or dep_id in circular_tasks
                })
        
        return Response({
            'nodes': nodes,
            'edges': edges,
            'has_cycles': len(circular_tasks) > 0
        })
    
    @action(detail=False, methods=['get'])
    def dependency_graph(self, request):
        """GET /api/tasks/dependency_graph/"""
        tasks = Task.objects.all()
        
        # Build dependency map
        dep_map = {t.id: list(t.dependencies) for t in tasks}
        
        # Find circular dependencies
        circular_tasks = set()
        for task_id in dep_map.keys():
            if has_circular_dependency(task_id, dep_map):
                circular_tasks.add(task_id)
        
        # Build graph data
        nodes = []
        edges = []
        
        for task in tasks:
            nodes.append({
                'id': task.id,
                'title': task.title,
                'has_cycle': task.id in circular_tasks
            })
            
            for dep_id in task.dependencies:
                edges.append({
                    'from': dep_id,  # Dependency
                    'to': task.id,    # Task that depends on it
                    'has_cycle': task.id in circular_tasks or dep_id in circular_tasks
                })
        
        return Response({
            'nodes': nodes,
            'edges': edges,
            'has_cycles': len(circular_tasks) > 0
        })
    
    @action(detail=False, methods=['get'])
    def eisenhower_matrix(self, request):
        """GET /api/tasks/eisenhower_matrix/"""
        tasks = Task.objects.filter(is_completed=False)
        
        if not tasks.exists():
            return Response({
                'DO_FIRST': [],
                'SCHEDULE': [],
                'DELEGATE': [],
                'ELIMINATE': []
            })
        
        scorer = TaskScorer()
        all_tasks_list = list(tasks)
        
        # Categorize tasks
        matrix = {
            'DO_FIRST': [],
            'SCHEDULE': [],
            'DELEGATE': [],
            'ELIMINATE': []
        }
        
        for task in all_tasks_list:
            urgency = scorer.calculate_urgency(task.due_date, task.importance)
            is_urgent = urgency >= 70
            is_important = task.importance >= 7
            
            # Categorize
            if is_urgent and is_important:
                category = 'DO_FIRST'
            elif not is_urgent and is_important:
                category = 'SCHEDULE'
            elif is_urgent and not is_important:
                category = 'DELEGATE'
            else:
                category = 'ELIMINATE'
            
            serializer = TaskSerializer(task)
            task_data = serializer.data
            task_data['urgency'] = urgency
            
            matrix[category].append(task_data)
        
        return Response(matrix)