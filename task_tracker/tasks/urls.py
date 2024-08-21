from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, TaskViewSet, busy_employees, important_tasks

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('busy-employees/', busy_employees, name='busy-employees'),
    path('important-tasks/', important_tasks, name='important-tasks'),
]
