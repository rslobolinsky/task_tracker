# task_tracker_app

### Описание проекта

Трекер задач позволит компании эффективно управлять заданиями, назначенными сотрудникам, и обеспечивать прозрачность
процессов выполнения задач. Это поможет в равномерном распределении нагрузки между сотрудниками и своевременном
выполнении ключевых задач.

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)

### Технологии:
- python 3.11
- django 4.2.2
- djangorestframework 3.14.0
- nginx
- gunicorn
- PostgreSQL
- Docker

### Инструкция для развертывания проекта с использованием Docker:

1. Клонирование
2. Создание и активация виртуального окружения
3. Установка зависимостей
4. Запуск проекта

Клонирование проекта:
```
https://github.com/rslobolinsky/task_tracker.git
```
Запуск:

Для запуска проекта необходимо создать .env в директории (тут корневая директория вашего проекта), 
скопировать в него содержимое файла .env.example 

Запустить команду, указанную ниже из директории.
```
docker-compose up -d --build
```

### Автор проекта:
Слоболинский Роман Викторович
https://github.com/rslobolinsky

