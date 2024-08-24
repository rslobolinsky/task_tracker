from django.contrib import admin
from task_tracker.models import Task, Employee


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'assignee', 'status', 'deadline')
    search_fields = ('name',)
    list_filter = ('status', 'deadline')
    ordering = ('deadline',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'additional_info', 'created_at', 'updated_at')
    search_fields = ('full_name', 'position')
    list_filter = ('additional_info', 'position', 'created_at', 'updated_at')
    ordering = ('full_name', 'created_at', 'updated_at')