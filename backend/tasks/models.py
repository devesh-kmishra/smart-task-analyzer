from django.db import models
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
        """Validate dependencies don't create cycles"""
        if self.pk and self.pk in self.dependencies:
            raise ValidationError("A task cannot depend on itself")