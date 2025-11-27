from django.test import TestCase
from datetime import date, timedelta
from .models import Task
from .scoring import TaskScorer, has_circular_dependency


class TaskScorerTestCase(TestCase):
    """For the TaskScorer algorithm"""
    
    def setUp(self):
        """Set up test data that will be used across multiple tests"""
        self.scorer = TaskScorer()
        
        # Create test tasks with different characteristics
        self.urgent_important_task = Task.objects.create(
            title="Critical Bug Fix",
            due_date=date.today(),  # Due today - very urgent
            estimated_hours=2,
            importance=9,
            dependencies=[]
        )
        
        self.important_not_urgent_task = Task.objects.create(
            title="Strategic Planning",
            due_date=date.today() + timedelta(days=30),  # Due in a month
            estimated_hours=5,
            importance=9,
            dependencies=[]
        )
        
        self.urgent_not_important_task = Task.objects.create(
            title="Minor UI Tweak",
            due_date=date.today() + timedelta(days=1),  # Due tomorrow
            estimated_hours=1,
            importance=3,
            dependencies=[]
        )
        
        self.neither_urgent_nor_important_task = Task.objects.create(
            title="Optional Documentation",
            due_date=date.today() + timedelta(days=60),  # Due in 2 months
            estimated_hours=3,
            importance=2,
            dependencies=[]
        )
        
        self.overdue_task = Task.objects.create(
            title="Overdue Report",
            due_date=date.today() - timedelta(days=5),  # 5 days overdue
            estimated_hours=4,
            importance=7,
            dependencies=[]
        )
    
    def test_urgency_calculation(self):
        """
        Test 1: Urgency Score Calculation
        Verifies that tasks are scored correctly based on their due dates
        """
        print("\n=== Test 1: Urgency Calculation ===")
        
        # Overdue tasks should get atleast 80 urgency
        overdue_urgency = self.scorer.calculate_urgency(self.overdue_task.due_date)
        print(f"Overdue task urgency: {overdue_urgency}")
        self.assertGreaterEqual(overdue_urgency, 80, "Overdue tasks should have urgency of 100")
        
        # Due today should get 95
        today_urgency = self.scorer.calculate_urgency(date.today())
        print(f"Due today urgency: {today_urgency}")
        self.assertEqual(today_urgency, 95, "Tasks due today should have urgency of 95")
        
        # Due in 1 week should be less urgent than due today
        week_urgency = self.scorer.calculate_urgency(date.today() + timedelta(days=7))
        print(f"Due in 1 week urgency: {week_urgency}")
        self.assertLess(week_urgency, today_urgency, "Tasks due in a week should be less urgent than today")
        self.assertGreater(week_urgency, 0, "Tasks due in a week should still have some urgency")
        
        # Far future tasks should have low urgency
        future_urgency = self.scorer.calculate_urgency(date.today() + timedelta(days=60))
        print(f"Due in 60 days urgency: {future_urgency}")
        self.assertLess(future_urgency, 20, "Far future tasks should have low urgency")
        
        print("✅ All urgency calculations passed!")
    
    def test_priority_score_calculation(self):
        """
        Test 2: Overall Priority Score Calculation
        Verifies that the weighted algorithm produces logical priority scores
        """
        print("\n=== Test 2: Priority Score Calculation ===")
        
        all_tasks = list(Task.objects.all())
        
        # Calculate scores for all test tasks
        urgent_important_score = self.scorer.calculate_priority_score(
            self.urgent_important_task, all_tasks
        )
        important_not_urgent_score = self.scorer.calculate_priority_score(
            self.important_not_urgent_task, all_tasks
        )
        urgent_not_important_score = self.scorer.calculate_priority_score(
            self.urgent_not_important_task, all_tasks
        )
        neither_score = self.scorer.calculate_priority_score(
            self.neither_urgent_nor_important_task, all_tasks
        )
        overdue_score = self.scorer.calculate_priority_score(
            self.overdue_task, all_tasks
        )
        
        print(f"Urgent & Important (due today, importance 9): {urgent_important_score}")
        print(f"Important but not urgent (due in 30 days, importance 9): {important_not_urgent_score}")
        print(f"Urgent but not important (due tomorrow, importance 3): {urgent_not_important_score}")
        print(f"Neither urgent nor important (due in 60 days, importance 2): {neither_score}")
        print(f"Overdue task (5 days overdue, importance 7): {overdue_score}")
        
        # Urgent AND important should score highest
        self.assertGreater(
            urgent_important_score, 
            important_not_urgent_score,
            "Urgent + Important should score higher than just Important"
        )
        
        # Overdue tasks should have very high scores
        self.assertGreater(
            overdue_score,
            neither_score,
            "Overdue tasks should score higher than low priority tasks"
        )
        
        # Tasks that are neither urgent nor important should score lowest
        self.assertLess(
            neither_score,
            urgent_important_score,
            "Low priority tasks should score lower than high priority"
        )
        
        # Score should be between 0 and 100
        for score in [urgent_important_score, important_not_urgent_score, 
                      urgent_not_important_score, neither_score, overdue_score]:
            self.assertGreaterEqual(score, 0, "Score should not be negative")
            self.assertLessEqual(score, 100, "Score should not exceed 100")
        
        print("✅ All priority score calculations passed!")
    
    def test_effort_and_dependency_scoring(self):
        """
        Test 3: Effort Score and Dependency Impact
        Verifies that quick wins and blocking tasks are prioritized correctly
        """
        print("\n=== Test 3: Effort and Dependency Scoring ===")
        
        # Create tasks with dependencies
        blocker_task = Task.objects.create(
            title="API Endpoint Development",
            due_date=date.today() + timedelta(days=7),
            estimated_hours=6,
            importance=8,
            dependencies=[]
        )
        
        dependent_task_1 = Task.objects.create(
            title="Frontend Integration",
            due_date=date.today() + timedelta(days=8),
            estimated_hours=4,
            importance=7,
            dependencies=[blocker_task.id]
        )
        
        dependent_task_2 = Task.objects.create(
            title="Mobile App Integration",
            due_date=date.today() + timedelta(days=9),
            estimated_hours=5,
            importance=7,
            dependencies=[blocker_task.id]
        )
        
        quick_win_task = Task.objects.create(
            title="Quick Bug Fix",
            due_date=date.today() + timedelta(days=7),
            estimated_hours=0.5,  # 30 minutes - quick win
            importance=6,
            dependencies=[]
        )
        
        long_task = Task.objects.create(
            title="Complete Refactor",
            due_date=date.today() + timedelta(days=7),
            estimated_hours=20,  # Long task
            importance=6,
            dependencies=[]
        )
        
        all_tasks = list(Task.objects.all())
        
        # Test effort scoring
        quick_effort_score = self.scorer.calculate_effort_score(0.5)
        medium_effort_score = self.scorer.calculate_effort_score(4)
        long_effort_score = self.scorer.calculate_effort_score(20)
        
        print(f"Quick task (0.5h) effort score: {quick_effort_score}")
        print(f"Medium task (4h) effort score: {medium_effort_score}")
        print(f"Long task (20h) effort score: {long_effort_score}")
        
        self.assertGreater(
            quick_effort_score,
            long_effort_score,
            "Quick tasks should have higher effort scores (quick wins)"
        )
        
        # Test dependency scoring
        blocker_dep_score = self.scorer.calculate_dependency_score(blocker_task, all_tasks)
        non_blocker_dep_score = self.scorer.calculate_dependency_score(quick_win_task, all_tasks)
        
        print(f"\nBlocker task (blocks 2 tasks) dependency score: {blocker_dep_score}")
        print(f"Non-blocker task dependency score: {non_blocker_dep_score}")
        
        self.assertGreater(
            blocker_dep_score,
            non_blocker_dep_score,
            "Tasks that block others should have higher dependency scores"
        )
        
        # Verify that blocking task gets priority boost in overall score
        blocker_priority = self.scorer.calculate_priority_score(blocker_task, all_tasks)
        similar_task_priority = self.scorer.calculate_priority_score(long_task, all_tasks)
        
        print(f"\nBlocker task overall priority: {blocker_priority}")
        print(f"Similar task (no blocking) overall priority: {similar_task_priority}")
        
        # Blocker should score higher than similar task due to dependency weight
        self.assertGreater(
            blocker_priority,
            similar_task_priority,
            "Blocking tasks should get priority boost"
        )
        
        print("✅ All effort and dependency tests passed!")


class CircularDependencyTestCase(TestCase):
    """Test cases for circular dependency detection"""
    
    def test_circular_dependency_detection(self):
        """
        Bonus Test: Circular Dependency Detection
        Verifies that circular dependencies are correctly identified
        """
        print("\n=== Bonus Test: Circular Dependency Detection ===")
        
        # Create tasks that form a circular dependency
        task_a = Task.objects.create(
            title="Task A",
            due_date=date.today() + timedelta(days=5),
            estimated_hours=2,
            importance=5,
            dependencies=[]
        )
        
        task_b = Task.objects.create(
            title="Task B",
            due_date=date.today() + timedelta(days=6),
            estimated_hours=3,
            importance=6,
            dependencies=[task_a.id]
        )
        
        task_c = Task.objects.create(
            title="Task C",
            due_date=date.today() + timedelta(days=7),
            estimated_hours=4,
            importance=7,
            dependencies=[task_b.id]
        )
        
        # Create circular dependency: A -> B -> C -> A
        task_a.dependencies = [task_c.id]
        task_a.save()
        
        # Build dependency map
        all_tasks = Task.objects.all()
        dep_map = {t.id: list(t.dependencies) for t in all_tasks}
        
        print(f"Dependency map: {dep_map}")
        
        # Test that circular dependency is detected
        has_cycle_a = has_circular_dependency(task_a.id, dep_map)
        has_cycle_b = has_circular_dependency(task_b.id, dep_map)
        has_cycle_c = has_circular_dependency(task_c.id, dep_map)
        
        print(f"Task A has cycle: {has_cycle_a}")
        print(f"Task B has cycle: {has_cycle_b}")
        print(f"Task C has cycle: {has_cycle_c}")
        
        self.assertTrue(has_cycle_a, "Circular dependency should be detected for Task A")
        self.assertTrue(has_cycle_b, "Circular dependency should be detected for Task B")
        self.assertTrue(has_cycle_c, "Circular dependency should be detected for Task C")
        
        # Test a task without circular dependency
        task_d = Task.objects.create(
            title="Task D - Independent",
            due_date=date.today() + timedelta(days=8),
            estimated_hours=2,
            importance=5,
            dependencies=[]
        )
        
        dep_map[task_d.id] = []
        has_cycle_d = has_circular_dependency(task_d.id, dep_map)
        
        print(f"Task D (independent) has cycle: {has_cycle_d}")
        
        self.assertFalse(has_cycle_d, "Independent task should not have circular dependency")
        
        print("✅ Circular dependency detection passed!")