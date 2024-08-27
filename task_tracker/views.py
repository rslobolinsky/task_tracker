from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from prompt_toolkit.validation import ValidationError
from rest_framework import viewsets, generics
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, CreateAPIView
from rest_framework.permissions import AllowAny

from .models import Employee, Task
from .serializers import EmployeeSerializer, TaskSerializer, BusyEmployeeSerializer, \
    TaskWithPotentialEmployeesSerializer

from django.db.models import Count, Q, Min


class EmployeeCreateAPIView(generics.CreateAPIView):
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


class BusyEmployeesListAPIView(ListAPIView):
    serializer_class = BusyEmployeeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Агрегируем данные о задачах для каждого сотрудника
        employees = Employee.objects.annotate(
            active_task_count=Count('task', filter=Q(task__status__in=['New Task', 'In Progress'])),
            earliest_deadline=Min('task__deadline', filter=Q(task__status__in=['New Task', 'In Progress']))
        ).order_by('-active_task_count', 'earliest_deadline')

        return employees


class TaskCreateAPIView(CreateAPIView):
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
            openapi.Parameter('sub_tasks', openapi.IN_QUERY, description="Фильтрация задач по наличию подзадач",
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
        requested_filters = set(self.request.query_params.keys()) - {'sub_tasks', 'has_task'}
        invalid_filters = requested_filters - allowed_filters

        if invalid_filters:
            raise ValidationError(f"Фильтрация по полю(-ям) {', '.join(invalid_filters)} невозможна."
                                  f"Доступные поля для фильтрации: {', '.join(allowed_filters)}")

        # Фильтрация по наличию подзадач
        subtasks_param = self.request.query_params.get('sub_tasks')
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
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [AllowAny]


class TaskDestroyAPIView(DestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [AllowAny]


class ImportantTasksListAPIView(ListAPIView):
    serializer_class = TaskWithPotentialEmployeesSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Задачи без назначений
        tasks_without_assignee = Task.objects.filter(
            assignee__isnull=True
        )

        # Задачи с родительской задачей в статусе 'In Progress'
        parent_tasks_in_progress = Task.objects.filter(
            Q(parent_task__isnull=False) &
            Q(parent_task__status='In Progress')
        )

        # Используем Q-объекты для объединения запросов
        queryset = Task.objects.filter(
            Q(id__in=tasks_without_assignee.values('id')) |
            Q(id__in=parent_tasks_in_progress.values('id'))
        ).distinct()

        return queryset
