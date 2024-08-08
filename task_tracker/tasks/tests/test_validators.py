from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from task_tracker.tasks.models import Employee, Task


class EmployeeValidationTest(APITestCase):

    def test_create_employee_with_short_name(self):
        url = reverse('employee-list')
        data = {'full_name': 'Jo', 'position': 'Developer'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('full_name', response.data)
        self.assertEqual(response.data['full_name'][0], "Full name must be at least 3 characters long.")

    def test_create_employee_with_short_position(self):
        url = reverse('employee-list')
        data = {'full_name': 'John Doe', 'position': 'D'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('position', response.data)
        self.assertEqual(response.data['position'][0], "Position must be at least 2 characters long.")


class TaskValidationTest(APITestCase):

    def test_create_task_with_short_name(self):
        url = reverse('task-list')
        employee = Employee.objects.create(full_name='Jane Doe', position='Manager')
        data = {'name': 'Ta', 'assignee': employee.id, 'deadline': '2024-12-31', 'status': 'Not Started'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertEqual(response.data['name'][0], "Task name must be at least 3 characters long.")

    def test_create_task_with_past_deadline(self):
        url = reverse('task-list')
        employee = Employee.objects.create(full_name='Jane Doe', position='Manager')
        data = {'name': 'Task 1', 'assignee': employee.id, 'deadline': '2020-12-31', 'status': 'Not Started'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('deadline', response.data)
        self.assertEqual(response.data['deadline'][0], "Deadline cannot be in the past.")

    def test_create_task_with_invalid_status(self):
        url = reverse('task-list')
        employee = Employee.objects.create(full_name='Jane Doe', position='Manager')
        data = {'name': 'Task 1', 'assignee': employee.id, 'deadline': '2024-12-31', 'status': 'Invalid Status'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(response.data['non_field_errors'][0], "Invalid status.")
