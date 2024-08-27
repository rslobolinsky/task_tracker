from django.utils import timezone
from datetime import timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from task_tracker.models import Employee, Task
from task_tracker.serializers import EmployeeSerializer, TaskSerializer, TaskSummarySerializer, \
    PotentialEmployeeSerializer, TaskWithPotentialEmployeesSerializer, BusyEmployeeSerializer


class EmployeeSerializerTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(full_name="John Doe", position="Developer")

    def test_employee_serialization(self):
        serializer = EmployeeSerializer(self.employee)
        data = serializer.data
        self.assertEqual(data['full_name'], "John Doe")
        self.assertEqual(data['position'], "Developer")

    def test_active_task_count(self):
        Task.objects.create(name="Task 1", assignee=self.employee, deadline=timezone.now().date(), status="New Task")
        Task.objects.create(name="Task 2", assignee=self.employee, deadline=timezone.now().date(), status="In Progress")
        Task.objects.create(name="Task 3", assignee=self.employee, deadline=timezone.now().date(), status="Completed")

        serializer = EmployeeSerializer(self.employee)
        self.assertEqual(serializer.data['active_task_count'], 2)

    def test_tasks_serialization(self):
        Task.objects.create(name="Task 1", assignee=self.employee, deadline=timezone.now().date(), status="New Task")
        serializer = EmployeeSerializer(self.employee)
        self.assertEqual(len(serializer.data['tasks']), 1)


class TaskSummarySerializerTest(TestCase):

    def setUp(self):
        self.employee = Employee.objects.create(full_name="Jane Doe", position="Manager")
        self.task = Task.objects.create(name="Test Task", assignee=self.employee, deadline=timezone.now().date(),
                                        status="New Task")

    def test_task_summary_serialization(self):
        serializer = TaskSummarySerializer(self.task)
        data = serializer.data
        self.assertEqual(data['name'], "Test Task")
        self.assertIn('parent_task', data)  # Проверяем, что поле parent_task присутствует


class TaskSerializerTest(TestCase):

    def setUp(self):
        self.employee = Employee.objects.create(full_name="Jane Doe", position="Manager")
        self.task = Task.objects.create(name="Parent Task", assignee=self.employee, deadline=timezone.now().date(),
                                        status="New Task")

    def test_task_serialization(self):
        serializer = TaskSerializer(self.task)
        data = serializer.data
        self.assertEqual(data['name'], "Parent Task")
        self.assertEqual(data['assignee'], self.employee.id)

    def test_deadline_validation(self):
        data = {
            'name': 'Task',
            'assignee': self.employee.id,
            'deadline': timezone.now().date() - timezone.timedelta(days=1),
            'status': 'New Task'
        }
        serializer = TaskSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_status_validation(self):
        data = {
            'name': 'Task',
            'assignee': self.employee.id,
            'deadline': timezone.now().date() + timezone.timedelta(days=1),
            'status': 'Invalid Status'
        }
        serializer = TaskSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)


class PotentialEmployeeSerializerTest(TestCase):

    def setUp(self):
        self.employee = Employee.objects.create(full_name="Alice Smith", position="Designer")

    def test_potential_employee_serialization(self):
        serializer = PotentialEmployeeSerializer(self.employee)
        data = serializer.data
        self.assertEqual(data['full_name'], "Alice Smith")


class TaskWithPotentialEmployeesSerializerTest(TestCase):

    def setUp(self):
        self.employee1 = Employee.objects.create(full_name="Alice Smith", position="Designer")
        self.employee2 = Employee.objects.create(full_name="Bob Johnson", position="Developer")
        self.task = Task.objects.create(name="Test Task", assignee=self.employee1, deadline=timezone.now().date(),
                                        status="New Task")

    def test_get_potential_employees(self):
        serializer = TaskWithPotentialEmployeesSerializer(self.task)
        data = serializer.data
        self.assertIn('potential_employees', data)  # Проверяем, что поле потенциальных сотрудников присутствует


class BusyEmployeeSerializerTest(TestCase):

    def setUp(self):
        self.employee1 = Employee.objects.create(full_name="Alice Smith", position="Designer")
        self.employee2 = Employee.objects.create(full_name="Bob Johnson", position="Developer")

        Task.objects.create(name="Task 1", assignee=self.employee1, deadline=timezone.now().date(), status="New Task")
        Task.objects.create(name="Task 2", assignee=self.employee1, deadline=timezone.now().date(), status="In Progress")
        Task.objects.create(name="Task 3", assignee=self.employee1, deadline=timezone.now().date(), status="Completed")

        Task.objects.create(name="Task A", assignee=self.employee2, deadline=timezone.now().date(), status="Not Started")
        Task.objects.create(name="Task B", assignee=self.employee2, deadline=timezone.now().date(), status="Completed")

    def test_busy_employee_serialization(self):
        serializer1 = BusyEmployeeSerializer(self.employee1)
        data1 = serializer1.data
        self.assertEqual(data1['full_name'], "Alice Smith")
        self.assertEqual(data1['position'], "Designer")
        self.assertEqual(data1['active_task_count'], 2)
        self.assertEqual(len(data1['tasks']), 3)

        serializer2 = BusyEmployeeSerializer(self.employee2)
        data2 = serializer2.data
        self.assertEqual(data2['full_name'], "Bob Johnson")
        self.assertEqual(data2['position'], "Developer")
        self.assertEqual(data2['active_task_count'], 1)
        self.assertEqual(len(data2['tasks']), 2)

    def test_no_tasks_for_employee(self):
        employee3 = Employee.objects.create(full_name="Charlie Brown", position="Tester")
        serializer3 = BusyEmployeeSerializer(employee3)
        data3 = serializer3.data
        self.assertEqual(data3['full_name'], "Charlie Brown")
        self.assertEqual(data3['position'], "Tester")
        self.assertEqual(data3['active_task_count'], 0)
        self.assertEqual(len(data3['tasks']), 0)
