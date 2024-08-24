from django.test import TestCase
from task_tracker.models import Employee, Task


class EmployeeModelTest(TestCase):

    def test_create_employee(self):
        employee = Employee.objects.create(full_name="John Doe", position="Developer")
        self.assertEqual(employee.full_name, "John Doe")
        self.assertEqual(employee.position, "Developer")


class TaskModelTest(TestCase):

    def test_create_task(self):
        employee = Employee.objects.create(full_name="Jane Doe", position="Manager")
        task = Task.objects.create(name="Test Task", assignee=employee, deadline="2024-12-31", status="Not Started")
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(task.assignee.full_name, "Jane Doe")
        self.assertEqual(task.deadline, "2024-12-31")
        self.assertEqual(task.status, "Not Started")
