from django.utils import timezone
from django.test import TestCase
from task_tracker.models import Employee, Task


class EmployeeModelTest(TestCase):

    def setUp(self):
        # Создаем тестового сотрудника
        self.employee = Employee.objects.create(
            full_name="John Doe",
            position="Software Engineer",
            additional_info="Experienced in Django and React."
        )

    def test_employee_creation(self):
        # Проверяем, что сотрудник создан правильно
        self.assertEqual(self.employee.full_name, "John Doe")
        self.assertEqual(self.employee.position, "Software Engineer")
        self.assertEqual(self.employee.additional_info, "Experienced in Django and React.")
        self.assertIsNotNone(self.employee.created_at)  # Проверяем, что поле created_at не пустое
        self.assertIsNotNone(self.employee.updated_at)  # Проверяем, что поле updated_at не пустое

    def test_employee_string_representation(self):
        # Проверяем, что метод __str__ возвращает правильное значение
        self.assertEqual(str(self.employee), "John Doe")

    def test_employee_additional_info_blank(self):
        # Создаем сотрудника без дополнительной информации
        employee_without_info = Employee.objects.create(
            full_name="Jane Smith",
            position="Project Manager"
        )
        self.assertEqual(employee_without_info.additional_info, "")  # Проверяем, что поле пустое


class TaskModelTest(TestCase):
    def setUp(self):
        # Создаем тестового сотрудника
        self.employee = Employee.objects.create(
            full_name="John Doe",
            position="Software Engineer"
        )

        # Создаем тестовую задачу
        self.task = Task.objects.create(
            name="Test Task",
            assignee=self.employee,
            deadline=timezone.now().date(),
            status='New Task'
        )

    def test_task_creation(self):
        # Проверяем, что задача создана правильно
        self.assertEqual(self.task.name, "Test Task")
        self.assertEqual(self.task.assignee, self.employee)
        self.assertIsNotNone(self.task.deadline)  # Проверяем, что поле deadline не пустое
        self.assertEqual(self.task.status, 'New Task')
        self.assertIsNotNone(self.task.created_at)  # Проверяем, что поле created_at не пустое
        self.assertIsNotNone(self.task.updated_at)  # Проверяем, что поле updated_at не пустое

    def test_task_string_representation(self):
        # Проверяем, что метод __str__ возвращает правильное значение
        self.assertEqual(str(self.task), "Test Task")

    def test_task_with_parent_task(self):
        # Создаем родительскую задачу
        parent_task = Task.objects.create(
            name="Parent Task",
            assignee=self.employee,
            deadline=timezone.now().date(),
            status='Not Started'
        )

        # Создаем дочернюю задачу
        sub_task = Task.objects.create(
            name="Sub Task",
            parent_task=parent_task,
            assignee=self.employee,
            deadline=timezone.now().date(),
            status='In Progress'
        )

        self.assertEqual(sub_task.parent_task, parent_task)  # Проверяем связь с родительской задачей
        self.assertIn(sub_task, parent_task.sub_tasks.all())  # Проверяем, что дочерняя задача включена в родительскую

    def test_task_status_choices(self):
        # Проверяем допустимые значения для статуса
        for status in Task.STATUS_CHOICES:
            self.assertIn(status[0], [choice[0] for choice in Task.STATUS_CHOICES])  # Проверяем наличие статусов
