import logging

from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from prompt_toolkit.validation import ValidationError
from rest_framework import viewsets, status
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .models import Employee, Task
from .serializers import EmployeeSerializer, TaskSerializer, ImportantTaskSerializer, BusyEmployeeSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Q

logger = logging.getLogger(__name__)


class EmployeeCreateAPIView(CreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [AllowAny]


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeListAPIView(ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]


class EmployeeRetrieveAPIView(RetrieveAPIView):
    queryset = Employee.objects.all()
    serializer_class = BusyEmployeeSerializer
    permission_classes = [AllowAny]


class EmployeeUpdateAPIView(UpdateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [AllowAny]


class EmployeeDestroyAPIView(DestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [AllowAny]


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


@api_view(['GET'])
def busy_employees(request):
    employees = Employee.objects.annotate(task_count=Count('task')).order_by('-task_count')
    data = [{'employee': emp.full_name, 'task_count': emp.task_count} for emp in employees]
    return Response(data)


class TaskCreateAPIView(CreateAPIView):
    """
    Контроллер создания новой задачи.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [AllowAny]


class TaskListAPIView(ListAPIView):
    queryset = Task.objects.all().order_by('id')
    serializer_class = TaskSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['assignee', 'status', 'parent_task', 'deadline']

    @swagger_auto_schema(
        operation_description="Получение списка задач с возможностью фильтрации по параметрам",
        manual_parameters=[
            openapi.Parameter('assignee', openapi.IN_QUERY, description="ID сотрудника", type=openapi.TYPE_INTEGER),
            openapi.Parameter('status', openapi.IN_QUERY, description="Статус задачи", type=openapi.TYPE_STRING),
            openapi.Parameter('parent_task', openapi.IN_QUERY, description="ID родительской задачи",
                              type=openapi.TYPE_INTEGER),
            openapi.Parameter('deadline', openapi.IN_QUERY, description="Дата выполнения задачи",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('subt_asks', openapi.IN_QUERY, description="Фильтрация задач по наличию подзадач",
                              type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('has_parent', openapi.IN_QUERY,
                              description="Фильтрация задач по наличию родительской задачи",
                              type=openapi.TYPE_BOOLEAN),
        ]
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        # Проверка на допустимость фильтров
        allowed_filters = set(self.filterset_fields)
        requested_filters = set(self.request.query_params.keys()) - {'subtasks', 'has_parent'}
        invalid_filters = requested_filters - allowed_filters

        if invalid_filters:
            raise ValidationError(f"Фильтрация по полю(-ям) {', '.join(invalid_filters)} невозможна. "
                                  f"Доступные поля для фильтрации: {', '.join(allowed_filters)}")

        # Фильтрация по наличию подзадач
        subtasks_param = self.request.query_params.get('subtasks')
        if subtasks_param is not None:
            if subtasks_param.lower() in ('true', '1'):
                queryset = queryset.filter(subtasks__isnull=False).distinct()
            elif subtasks_param.lower() in ('false', '0'):
                queryset = queryset.filter(subtasks__isnull=True).distinct()

        # Фильтрация по наличию родительской задачи
        has_parent_param = self.request.query_params.get('has_parent')
        if has_parent_param is not None:
            if has_parent_param.lower() in ('true', '1'):
                queryset = queryset.filter(parent_task__isnull=False)
            elif has_parent_param.lower() in ('false', '0'):
                queryset = queryset.filter(parent_task__isnull=True)

        return queryset


class TaskRetrieveAPIView(RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [AllowAny]


class TaskUpdateAPIView(UpdateAPIView):
    """
    Контроллер для обновления данных одной задачи по указанному id.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [AllowAny]


class TaskDestroyAPIView(DestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [AllowAny]


# @api_view(['GET'])
# def important_tasks(request):
#     # Найти задачи, которые не взяты в работу, но от которых зависят задачи, взятые в работу
#     important_tasks = Task.objects.filter(
#         status='not started',
#         sub_tasks__status='in progress'
#     ).distinct()

# Найти сотрудников с наименьшим количеством активных задач
# employees = Employee.objects.annotate(
#     active_tasks=Count('task', filter=Q(task__status='in progress'))
# ).order_by('active_tasks')
#
# if not important_tasks.exists():
#     return Response({'message': 'No important task_tracker found.'}, status=status.HTTP_404_NOT_FOUND)
#
# if not employees.exists():
#     return Response({'message': 'No available employees found.'}, status=status.HTTP_404_NOT_FOUND)
#
# min_task_count = employees.first().active_tasks
# result = []
#
# for task in important_tasks:
#     potential_employees = employees.filter(
#         Q(active_tasks__lte=min_task_count + 2) | Q(id=task.parent_task.assignee_id)
#     )
#     employee_names = [emp.full_name for emp in potential_employees]
#
#     result.append({
#         'task': task.title,
#         'deadline': task.deadline,
#         'employees': employee_names
#     })

# return Response(status=status.HTTP_200_OK)

# @api_view(['GET'])
# def important_tasks(request):
#     unassigned_tasks = Task.objects.filter(status='Not Started', sub_tasks__status='In Progress').distinct()
#     least_loaded_employee = Employee.objects.annotate(task_count=Count('task')).order_by('task_count').first()
#     # important_tasks = []
#     # if not least_loaded_employee:
#     #     return Response([])
#
#     for task in unassigned_tasks:
#         candidates = Employee.objects.annotate(task_count=Count('task')).filter(
#             Q(task_count__lte=least_loaded_employee.task_count + 2) |
#             Q(task__in=task.parent_task.sub_tasks.all())
#         )
#         important_tasks.append({
#             'task': task.name,
#             'deadline': task.deadline,
#             'candidates': [emp.full_name for emp in candidates]
#         })
#     return Response(important_tasks)

# @api_view(['GET'])
# def important_tasks(request):
#     task = Task.objects.filter(
#         status="Not Started",
#         parent_task__isnull=False,
#         parent_task__status="In Progress"
#     )
#     return Response(task)
#
#
# class TaskViewSet(viewsets.ModelViewSet):
#     queryset = Task.objects.all()
#     serializer_class = TaskSerializer
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         id = self.request.query_params.get('id', None)
#         if id is not None:
#             try:
#                 queryset = queryset.filter(id=int(id))
#             except ValueError:
#                 # Обработайте ошибку или верните пустой результат
#                 queryset = queryset.none()
#         return queryset

class ImportantTasksListAPIView(ListAPIView):
    serializer_class = ImportantTaskSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Возвращает список задач, которые не взяты в работу (статус 'new'),
        но от которых зависят другие задачи, находящиеся в работе.
        """
        important_tasks = Task.objects.filter(
            status='New Task',
            parent_task__status='In Progress'
        )

        return important_tasks
