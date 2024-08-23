import logging
from rest_framework import viewsets, status
from rest_framework.views import APIView

from .models import Employee, Task
from .serializers import EmployeeSerializer, TaskSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Q

logger = logging.getLogger(__name__)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


@api_view(['GET'])
def busy_employees(request):
    employees = Employee.objects.annotate(task_count=Count('task')).order_by('-task_count')
    data = [{'employee': emp.full_name, 'task_count': emp.task_count} for emp in employees]
    return Response(data)


@api_view(['GET'])
def important_tasks(request):
    # Найти задачи, которые не взяты в работу, но от которых зависят задачи, взятые в работу
    important_tasks = Task.objects.filter(
        status='not started',
        sub_tasks__status='in progress'
    ).distinct()

    # Найти сотрудников с наименьшим количеством активных задач
    employees = Employee.objects.annotate(
        active_tasks=Count('task', filter=Q(task__status='in progress'))
    ).order_by('active_tasks')

    if not important_tasks.exists():
        return Response({'message': 'No important tasks found.'}, status=status.HTTP_404_NOT_FOUND)

    if not employees.exists():
        return Response({'message': 'No available employees found.'}, status=status.HTTP_404_NOT_FOUND)

    min_task_count = employees.first().active_tasks
    result = []

    for task in important_tasks:
        potential_employees = employees.filter(
            Q(active_tasks__lte=min_task_count + 2) | Q(id=task.parent_task.assignee_id)
        )
        employee_names = [emp.full_name for emp in potential_employees]

        result.append({
            'task': task.title,
            'deadline': task.deadline,
            'employees': employee_names
        })

    return Response(result, status=status.HTTP_200_OK)

