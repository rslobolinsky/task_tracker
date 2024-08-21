from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from tasks.models import Employee, Task


class SpecialEndpointsAPITest(APITestCase):

    def setUp(self):
        self.employee1 = Employee.objects.create(full_name='John Doe', position='Developer')
        self.employee2 = Employee.objects.create(full_name='Jane Doe', position='Manager')
        self.task1 = Task.objects.create(name='Task 1', assignee=self.employee1, deadline='2024-12-31',
                                         status='In Progress')
        self.task2 = Task.objects.create(name='Task 2', parent_task=self.task1, deadline='2024-12-31',
                                         status='Not Started')


    def test_busy_employees(self):
        url = reverse('busy-employees')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Проверка, что сотрудник с наибольшим количеством задач идет первым
        self.assertEqual(response.data[0]['employee'], 'John Doe')
        self.assertEqual(response.data[0]['task_count'], 1)
        self.assertEqual(response.data[1]['employee'], 'Jane Doe')
        self.assertEqual(response.data[1]['task_count'], 0)


