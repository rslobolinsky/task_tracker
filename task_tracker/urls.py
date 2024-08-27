from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter

from task_tracker.apps import TaskConfig
from .views import ImportantTasksListAPIView, TaskListAPIView, \
    TaskCreateAPIView, TaskRetrieveAPIView, TaskUpdateAPIView, TaskDestroyAPIView, EmployeeListAPIView, \
    EmployeeCreateAPIView, EmployeeRetrieveAPIView, EmployeeUpdateAPIView, EmployeeDestroyAPIView, \
    BusyEmployeesListAPIView

app_name = TaskConfig.name

router = SimpleRouter()


urlpatterns = [
    path('', include(router.urls)),
    path('employees/', EmployeeListAPIView.as_view(), name='employee-list'),
    path('employees/create/', EmployeeCreateAPIView.as_view(), name='employee-create'),
    path('employees/<int:pk>/', EmployeeRetrieveAPIView.as_view(), name='employee-detail'),
    path('employees/<int:pk>/update/', EmployeeUpdateAPIView.as_view(), name='employee-update'),
    path('employees/<int:pk>/delete/', EmployeeDestroyAPIView.as_view(), name='employee-delete'),

    path('employees/busy/', BusyEmployeesListAPIView.as_view(), name='busy-employees'),

    path('tasks/', TaskListAPIView.as_view(), name='task-list'),
    path('tasks/create/', TaskCreateAPIView.as_view(), name='task-create'),
    path('tasks/<int:pk>/', TaskRetrieveAPIView.as_view(), name='task-detail'),
    path('tasks/<int:pk>/update/', TaskUpdateAPIView.as_view(), name='task-update'),
    path('tasks/<int:pk>/delete/', TaskDestroyAPIView.as_view(), name='task-delete'),
    path('tasks/important/', ImportantTasksListAPIView.as_view(), name='important-tasks'),
]


