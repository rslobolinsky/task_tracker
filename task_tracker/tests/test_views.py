from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from task_tracker.models import Employee, Task


class EmployeeAPITest(APITestCase):

    def test_create_employee(self):
        url = reverse('employee-list')
        data = {'full_name': 'John Doe', 'position': 'Developer'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 1)
        self.assertEqual(Employee.objects.get().full_name, 'John Doe')

    def test_get_employees(self):
        Employee.objects.create(full_name='John Doe', position='Developer')
        url = reverse('employee-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['full_name'], 'John Doe')


class TaskAPITest(APITestCase):

    def test_create_task(self):
        employee = Employee.objects.create(full_name='Jane Doe', position='Manager')
        url = reverse('task-list')
        data = {'name': 'Test Task', 'assignee': employee.id, 'deadline': '2024-12-31', 'status': 'Not Started'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.get().name, 'Test Task')

    def test_get_tasks(self):
        employee = Employee.objects.create(full_name='Jane Doe', position='Manager')
        Task.objects.create(name='Test Task', assignee=employee, deadline='2024-12-31', status='Not Started')
        url = reverse('task-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Task')
