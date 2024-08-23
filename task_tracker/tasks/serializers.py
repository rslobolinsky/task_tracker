from django.utils import timezone

from rest_framework import serializers, viewsets
from .models import Employee, Task


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'position']

    # Проверяет, что имя сотрудника содержит не менее 3 символов.
    def validate_full_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Full name must be at least 3 characters long.")
        return value

    # Проверяет, что должность сотрудника содержит не менее 2 символов.
    def validate_position(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Position must be at least 2 characters long.")
        return value


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name', 'parent_task', 'assignee', 'deadline', 'status']

    # Проверяет, что название задачи содержит не менее 3 символов
    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Task name must be at least 3 characters long.")
        return value

    # Проверяет, что дедлайн задачи не находится в прошлом.
    def validate_deadline(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value

    # Проверяет, что статус задачи является одним из допустимых значений ('Not Started', 'In Progress', 'Completed').
    def validate(self, data):
        if data['status'] not in ['Not Started', 'In Progress', 'Completed']:
            raise serializers.ValidationError("Invalid status.")
        return data

    def update(self, instance, validated_data):
        instance.assignee = validated_data.get('assignee', instance.assignee)
        if 'status' in validated_data:
            instance.status = validated_data['status']
        instance.save()
        return instance


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        id = self.request.query_params.get('id', None)
        if id is not None:
            try:
                queryset = queryset.filter(id=int(id))
            except ValueError:
                # Обработайте ошибку или верните пустой результат
                queryset = queryset.none()
        return queryset
