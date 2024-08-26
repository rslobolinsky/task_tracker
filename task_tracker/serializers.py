from django.db.models import Count, Min, Q
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from .models import Employee, Task


class EmployeeSerializer(ModelSerializer):
    active_task_count = SerializerMethodField()
    tasks = SerializerMethodField()

    def get_tasks(self, employee):
        tasks = Task.objects.filter(assignee=employee, status__in=['New Task', 'In Progress'])
        return TaskSummarySerializer(tasks, many=True).data

    def get_active_task_count(self, employee):
        return Task.objects.filter(assignee=employee, status__in=['New Task', 'In Progress']).count()

    def validate_full_name(self, value):
        if not value.isalpha():
            raise ValidationError("Имя должно содержать только буквы.")
        return value

    def validate_position(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Position must be at least 2 characters long.")
        return value

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'position', 'active_task_count', 'tasks']


class TaskSummarySerializer(ModelSerializer):
    parent_task = SerializerMethodField()

    def get_parent_task(self, task):
        if task.parent_task:
            return {
                'id': task.parent_task.id,
                'name': task.parent_task.name,
                'deadline': task.parent_task.deadline
            }
        return None

    class Meta:
        model = Task
        fields = ['id', 'name', 'deadline', 'status', 'parent_task']

class BusyEmployeeSerializer(ModelSerializer):
    tasks = SerializerMethodField()
    active_task_count = SerializerMethodField()

    def get_tasks(self, employee):
        # Возвращаем все задачи, назначенные сотруднику
        tasks = Task.objects.filter(assignee=employee)
        return TaskSummarySerializer(tasks, many=True).data

    def get_active_task_count(self, employee):
        # Считаем только задачи со статусом 'New Task' и 'In Progress'
        return Task.objects.filter(assignee=employee, status__in=['New Task', 'In Progress', 'Not Started']).count()

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'position', 'active_task_count', 'tasks']

class TaskSerializer(ModelSerializer):
    sub_tasks = SerializerMethodField()

    def get_sub_tasks(self, task):
        if task.sub_tasks.exists():
            return TaskSummarySerializer(task.sub_tasks.all(), many=True).data
        return []

    def validate_deadline(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value

    class Meta:
        model = Task
        fields = ['id', 'name', 'parent_task', 'assignee', 'deadline', 'status', 'sub_tasks']

    # Проверяет, что статус задачи является одним из допустимых значений ('Not Started', 'In Progress', 'Completed').
    def validate(self, data):
        if data['status'] not in ['New Task', 'In Progress', 'Not Started', 'Completed']:
            raise serializers.ValidationError("Invalid status.")
        return data


class PotentialEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'full_name']

class TaskWithPotentialEmployeesSerializer(serializers.ModelSerializer):
    potential_employees = serializers.SerializerMethodField()

    def get_potential_employees(self, task):
        # Получение всех сотрудников с количеством задач
        employees = Employee.objects.annotate(
            task_count=Count('task', filter=Q(task__status__in=['New Task', 'In Progress']))
        )

        # Находим минимальное количество задач у сотрудников
        min_task_count = employees.aggregate(min_task_count=Min('task_count'))['min_task_count']

        # Получаем сотрудников, которые могут взять задачу
        suitable_employees = employees.filter(
            Q(task_count__lte=min_task_count + 2) |
            Q(id__in=task.sub_tasks.values('assignee'))
        )

        return PotentialEmployeeSerializer(suitable_employees, many=True).data

    class Meta:
        model = Task
        fields = ['id', 'name', 'deadline', 'potential_employees']