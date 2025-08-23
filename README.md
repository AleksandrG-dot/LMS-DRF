# LMS-сервис

## Домашняя работа для урока: 30.2 Сериализаторы

### Применить миграции
`python manage.py migrate`

### Наполнение данными
`python manage.py add_courses` - добавление курсов  
`python manage.py add_lessons`  - добавление уроков  

Продолжаем работать с проектом от ДЗ 30.1
Здесь:
- добавлен вывод количества уроков в курсе "lesson_count" (изменен CourseSerializer, с использованием SerializerMethodField())
