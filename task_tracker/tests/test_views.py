from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from task_tracker.models import Employee, Task


class EmployeeCreateAPIViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('task_tracker:employee-create')  # Используйте правильный путь
        self.valid_data = {
            'full_name': 'John Doe',
            'position': 'Developer Dev',
        }

    def test_create_employee(self):
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class EmployeeListAPIViewTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('task_tracker:employee-list')
        self.employee = Employee.objects.create(
            full_name='John Doe',
            position='Developer',
            additional_info='Experienced'
        )

    def test_list_employees(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['full_name'], 'John Doe')


class EmployeeRetrieveAPIViewTestCase(APITestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            full_name='John Doe',
            position='Developer',
            additional_info='Experienced'
        )
        self.url = reverse('task_tracker:employee-detail', kwargs={'pk': self.employee.pk})

    def test_retrieve_employee(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'John Doe')


class EmployeeUpdateAPIViewTestCase(APITestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            full_name='John Doe',
            position='Developer',
            additional_info='Experienced'
        )
        self.url = reverse('task_tracker:employee-update', kwargs={'pk': self.employee.pk})
        self.valid_data = {
            'full_name': 'John Doe Updated',
            'position': 'Senior Developer',
            'additional_info': 'More experienced'
        }

    def test_update_employee(self):
        response = self.client.put(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.full_name, 'John Doe Updated')


class EmployeeDestroyAPIViewTestCase(APITestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            full_name='John Doe',
            position='Developer',
            additional_info='Experienced'
        )
        self.url = reverse('task_tracker:employee-delete', kwargs={'pk': self.employee.pk})

    def test_destroy_employee(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Employee.objects.count(), 0)


class TaskCreateAPIViewTestCase(APITestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            full_name='John Doe',
            position='Developer',
            additional_info='Experienced'
        )
        self.url = reverse('task_tracker:task-create')
        self.valid_data = {
            'name': 'New Task',
            'assignee': self.employee.id,
            'status': 'New Task',
            'deadline': '2024-12-31'
        }

    def test_create_task(self):
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.get().name, 'New Task')


class TaskListAPIViewTestCase(APITestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            full_name='John Doe',
            position='Developer',
            additional_info='Experienced'
        )
        self.url = reverse('task_tracker:task-list')
        self.task = Task.objects.create(
            name='Task 1',
            assignee=self.employee,
            status='New Task',
            deadline='2024-12-31'
        )

    def test_list_tasks(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Task 1')


class TaskRetrieveAPIViewTestCase(APITestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            full_name='John Doe',
            position='Developer',
            additional_info='Experienced'
        )
        self.task = Task.objects.create(
            name='Task 1',
            assignee=self.employee,
            status='New Task',
            deadline='2024-12-31'
        )
        self.url = reverse('task_tracker:task-detail', kwargs={'pk': self.task.pk})

    def test_retrieve_task(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Task 1')


class TaskUpdateAPIViewTestCase(APITestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            full_name='John Doe',
            position='Developer',
            additional_info='Experienced'
        )
        self.task = Task.objects.create(
            name='Task 1',
            assignee=self.employee,
            status='New Task',
            deadline='2024-12-31'
        )
        self.url = reverse('task_tracker:task-update', kwargs={'pk': self.task.pk})
        self.valid_data = {
            'name': 'Updated Task',
            'assignee': self.employee.id,
            'status': 'In Progress',
            'deadline': '2024-12-30'
        }

    def test_update_task(self):
        response = self.client.put(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, 'Updated Task')


class TaskDestroyAPIViewTestCase(APITestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            full_name='John Doe',
            position='Developer',
            additional_info='Experienced'
        )
        self.task = Task.objects.create(
            name='Task 1',
            assignee=self.employee,
            status='New Task',
            deadline='2024-12-31'
        )
        self.url = reverse('task_tracker:task-delete', kwargs={'pk': self.task.pk})

    def test_destroy_task(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)


class TaskFilterAPIViewTestCase(APITestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            full_name='John Doe',
            position='Developer',
            additional_info='Experienced'
        )
        self.url = reverse('task_tracker:task-list')
        self.task1 = Task.objects.create(
            name='Task 1',
            assignee=self.employee,
            status='New Task',
            deadline='2024-12-31'
        )
        self.task2 = Task.objects.create(
            name='Task 2',
            assignee=self.employee,
            status='In Progress',
            deadline='2023-12-31'
        )

    def test_filter_tasks_by_status(self):
        response = self.client.get(self.url, {'status': 'In Progress'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Task 2')

    # def test_filter_tasks_by_subtasks(self):
    #     # Assuming subtasks parameter filtering is added
    #     response = self.client.get(self.url, {'sub_tasks': 'true'})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)



class ImportantTasksListAPIViewTestCase(APITestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            full_name='John Doe',
            position='Developer',
            additional_info='Experienced'
        )
        self.url = reverse('task_tracker:important-tasks')
        self.task1 = Task.objects.create(
            name='Task without assignee',
            assignee=None,
            status='New Task',
            deadline='2024-12-31'
        )
        self.task2 = Task.objects.create(
            name='Task with in-progress parent',
            parent_task=self.task1,
            status='In Progress',
            deadline='2024-12-30'
        )

    def test_important_tasks(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
