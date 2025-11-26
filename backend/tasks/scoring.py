from datetime import date

class TaskScorer:
    def __init__(self, urgency_weight=0.35, importance_weight=0.30,
                 effort_weight=0.20, dependency_weight=0.15):
        self.urgency_weight = urgency_weight
        self.importance_weight = importance_weight
        self.effort_weight = effort_weight
        self.dependency_weight = dependency_weight
    
    def calculate_priority_score(self, task, all_tasks):
        """Calculate overall priority score (0-100)"""
        urgency = self.calculate_urgency(task.due_date)
        importance = self.calculate_importance(task.importance)
        effort = self.calculate_effort_score(task.estimated_hours)
        dependency = self.calculate_dependency_score(task, all_tasks)
        
        score = (
            urgency * self.urgency_weight +
            importance * self.importance_weight +
            effort * self.effort_weight +
            dependency * self.dependency_weight
        )
        
        return round(score, 2)
    
    def calculate_urgency(self, due_date):
        """Calculate urgency based on due date (0-100)"""
        if not due_date:
            return 20  # Default for tasks without due date
        
        today = date.today()
        days_until_due = (due_date - today).days
        
        # Overdue tasks
        if days_until_due < 0:
            return 100
        
        # Due today
        if days_until_due == 0:
            return 95
        
        # Due within a week
        if days_until_due <= 7:
            return 90 - (days_until_due * 10)
        
        # Due within a month
        if days_until_due <= 30:
            return max(20, 60 - (days_until_due - 7) * 2)
        
        # Far future
        return max(0, 20 - (days_until_due - 30) * 0.5)
    
    def calculate_importance(self, importance_rating):
        """Convert 1-10 importance to 0-100 scale"""
        return importance_rating * 10
    
    def calculate_effort_score(self, estimated_hours):
        """Quick wins get higher scores (0-100)"""
        if estimated_hours <= 1:
            return 90
        if estimated_hours <= 4:
            return 70 - (estimated_hours - 1) * 10
        return max(20, 50 - (estimated_hours - 4) * 5)
    
    def calculate_dependency_score(self, task, all_tasks):
        """Score based on how many tasks this blocks (0-100)"""
        blocked_count = sum(
            1 for t in all_tasks 
            if task.id in t.dependencies
        )
        
        if blocked_count == 0:
            return 0
        elif blocked_count == 1:
            return 30
        elif blocked_count == 2:
            return 60
        else:
            return 100
    
    def generate_suggestion_reason(self, task, all_tasks):
        """Generate human-readable explanation"""
        reasons = []
        
        urgency = self.calculate_urgency(task.due_date)
        if urgency >= 95:
            reasons.append("due today or overdue")
        elif urgency >= 70:
            reasons.append("due soon")
        
        if task.importance >= 8:
            reasons.append("high importance")
        
        if task.estimated_hours <= 1:
            reasons.append("quick win")
        
        blocked_count = sum(1 for t in all_tasks if task.id in t.dependencies)
        if blocked_count > 0:
            reasons.append(f"blocks {blocked_count} other task(s)")
        
        return " - ".join(reasons) if reasons else "good overall priority"