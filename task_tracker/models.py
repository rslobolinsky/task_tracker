from django.db import models
from prompt_toolkit.validation import ValidationError


class Employee(models.Model):
    full_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    additional_info = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.full_name


class Task(models.Model):
    STATUS_CHOICES = [
        ('New Task', 'New Task'),
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    name = models.CharField(max_length=200)
    parent_task = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_tasks')
    assignee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    deadline = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    additional_info = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    def clean(self):
        if self.parent_task and self.deadline > self.parent_task.deadline:
            raise ValidationError('Task deadline cannot be earlier than parent task deadline.')

    def save(self, *args, **kwargs):
        self.clean()
        super(Task, self).save(*args, **kwargs)
