from django.test import TestCase
from tasks.models import Employee, Task
from tasks.serializers import EmployeeSerializer, TaskSerializer

class EmployeeSerializerTest(TestCase):

    def test_employee_serialization(self):
        employee = Employee.objects.create(full_name="John Doe", position="Developer")
        serializer = EmployeeSerializer(employee)
        data = serializer.data
        self.assertEqual(data['full_name'], "John Doe")
        self.assertEqual(data['position'], "Developer")

class TaskSerializerTest(TestCase):

    def test_task_serialization(self):
        employee = Employee.objects.create(full_name="Jane Doe", position="Manager")
        task = Task.objects.create(name="Test Task", assignee=employee, deadline="2024-12-31", status="Not Started")
        serializer = TaskSerializer(task)
        data = serializer.data
        self.assertEqual(data['name'], "Test Task")
        self.assertEqual(data['assignee'], employee.id)
        self.assertEqual(data['deadline'], "2024-12-31")
        self.assertEqual(data['status'], "Not Started")
