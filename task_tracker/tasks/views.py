import logging
from rest_framework import viewsets
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
    unassigned_tasks = Task.objects.filter(status='Not Started', sub_tasks__status='In Progress').distinct()
    least_loaded_employee = Employee.objects.annotate(task_count=Count('task')).order_by('task_count').first()
    #important_tasks = []
    #if not least_loaded_employee:
        #return Response([])

    for task in unassigned_tasks:
        candidates = Employee.objects.annotate(task_count=Count('task')).filter(
            Q(task_count__lte=least_loaded_employee.task_count + 2) |
            Q(task__in=task.parent_task.sub_tasks.all())
        )
        important_tasks.append({
            'task': task.name,
            'deadline': task.deadline,
            'candidates': [emp.full_name for emp in candidates]
        })

    return Response(important_tasks)


class ImportantTasksView(APIView):
    def get(self, request, *args, **kwargs):
        important_tasks = Task.objects.filter(
            status='Not Started',
            parent_task__status='In Progress'
        )
        logger.debug(f'Important tasks: {important_tasks}')
        serializer = TaskSerializer(important_tasks, many=True)
        return Response(serializer.data)