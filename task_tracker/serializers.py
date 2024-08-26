from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from .models import Employee, Task


class EmployeeSerializer(ModelSerializer):
    active_task_count = SerializerMethodField()
    tasks = SerializerMethodField

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
        fields = ['id', 'full_name', 'position', 'active_task_count']


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
        tasks = Task.objects.filter(assignee=employee, status__in=['New Task', 'In Progress'])
        return TaskSummarySerializer(tasks, many=True).data

    def get_active_task_count(self, employee):
        return Task.objects.filter(assignee=employee, status__in=['New Task', 'In Progress']).count()

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'position', 'active_task_count', 'tasks']


class TaskSerializer(ModelSerializer):
    sub_tasks = SerializerMethodField()

    def get_tasks(self, employee):
        # Получаем задачи, назначенные на сотрудника
        tasks = Task.objects.filter(assignee=employee, status__in=['New Task', 'In Progress'])

        # Получаем родительские задачи для подзадач, назначенных на сотрудника
        parent_tasks = Task.objects.filter(sub_tasks__assignee=employee,
                                           sub_tasks__status__in=['New Task', 'In Progress']).distinct()

        # Объединяем две выборки
        all_tasks = tasks.union(parent_tasks)

        return TaskSerializer(all_tasks, many=True).data

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




class ImportantTaskSerializer(ModelSerializer):
    potential_employees = SerializerMethodField()

    def get_potential_employees(self, task):

        employees = Employee.objects.all()
        if not employees:
            return []

        # Определяем минимальное количество задач у сотрудников
        min_task_count = None
        for employee in employees:
            task_count = Task.objects.filter(assignee=employee).count()
            if min_task_count is None or task_count < min_task_count:
                min_task_count = task_count

        suitable_employees = []

        # Отбираем сотрудников, которые могут взять задачу
        for employee in employees:
            task_count = Task.objects.filter(assignee=employee).count()
            parent_task_employee = Task.objects.filter(parent_task=task, assignee=employee).exists()

            # Если сотрудник имеет минимальную загруженность или выполняет родительскую задачу,
            # и у него не более чем на 2 задачи больше, чем у наименее загруженного сотрудника
            if task_count == min_task_count or (parent_task_employee and task_count <= min_task_count + 2):
                employee_name = (f"{employee.full_name}. ID:{employee.id}").strip()
                if employee_name not in suitable_employees:
                    suitable_employees.append(employee_name)

        return suitable_employees

    class Meta:
        model = Task
        fields = ['id', 'name', 'deadline', 'potential_employees']
