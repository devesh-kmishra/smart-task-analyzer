from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class Task(models.Model):
    title = models.CharField(max_length=200)
    due_date = models.DateField()
    estimated_hours = models.FloatField(
        validators=[MinValueValidator(0.1)],
        help_text="Estimated hours to complete"
    )
    importance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Importance rating from 1-10"
    )
    dependencies = models.JSONField(
        default=list,
        blank=True,
        help_text="List of task IDs this task depends on"
    )
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    priority_score = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['-priority_score', 'due_date']
    
    def __str__(self):
        return self.title
    
    def clean(self):
        if self.importance and (self.importance < 1 or self.importance > 10):
            raise ValidationError('Importance must be between 1 and 10')
        if self.estimated_hours and self.estimated_hours < 0:
            raise ValidationError('Estimated hours cannot be negative')
        
        """Validate dependencies don't create cycles"""
        if self.pk and self.pk in self.dependencies:
            raise ValidationError("A task cannot depend on itself")
        
class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    urgency_weight = models.FloatField(default=0.35)
    importance_weight = models.FloatField(default=0.30)
    effort_weight = models.FloatField(default=0.20)
    dependency_weight = models.FloatField(default=0.15)

    class Meta:
        verbose_name_plural = "User Preferences"
    
    def __str__(self):
        return f"{self.user.username}'s preferences"
    
    def clean(self):
        total = (self.urgency_weight + self.importance_weight + 
                 self.effort_weight + self.dependency_weight)
        if not (0.99 <= total <= 1.01):  # Allow small floating point errors
            raise ValidationError('Weights must sum to 1.0')