from django.core.management.base import BaseCommand
from task_tracker.tasks.models import Employee, Task
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create initial data for the project'

    def handle(self, *args, **kwargs):
        employee1 = Employee.objects.create(full_name="Иван Иванов", position="Разработчик")
        employee2 = Employee.objects.create(full_name="Анна Смирнова", position="Менеджер проекта")
        employee3 = Employee.objects.create(full_name="Петр Петров", position="Тестировщик")

        task1 = Task.objects.create(
            name="Разработка API",
            assignee=employee1,
            deadline=timezone.now() + timezone.timedelta(days=10),
            status="Not Started"
        )

        task2 = Task.objects.create(
            name="Тестирование API",
            parent_task=task1,
            assignee=employee3,
            deadline=timezone.now() + timezone.timedelta(days=15),
            status="Not Started"
        )

        task3 = Task.objects.create(
            name="Написание документации",
            assignee=employee2,
            deadline=timezone.now() + timezone.timedelta(days=5),
            status="In Progress"
        )

        task4 = Task.objects.create(
            name="Обновление документации",
            parent_task=task3,
            assignee=employee2,
            deadline=timezone.now() + timezone.timedelta(days=20),
            status="Not Started"
        )

        task5 = Task.objects.create(
            name="Деплой приложения",
            assignee=employee1,
            deadline=timezone.now() + timezone.timedelta(days=30),
            status="Not Started"
        )

        self.stdout.write(self.style.SUCCESS('Successfully created initial data'))
