# LMS-сервис
API-cервис для создания обучающего контента. Позволяет создавать курсы, уроки в курсах, подписываться на обновления курсов, оплачивать курсы.
Для работы с сервисом требуется авторизация пользователя. 
Создано на Django REST Framework и БД PostgreSQL.

## Домашняя работа для уроков: 35.1 Серверы, Nginx и ручной деплой и 35.2 CI/CD и GitHub Actions

### URL-адреса  
`http://<your_server>/materials/course/` - курсы  
`http://<your_server>/materials/lesson/` - уроки  (id/, create/, id/delete/, id/update/)  
`http://<your_server>/users/` - пользователи (register/, login/, token/refresh/, list/, id/, id/update/, id/delete/)  
`http://<your_server>/users/payment/` - платежи  
`http://<your_server>/users/subs/` - управление подписками пользователей  
`http://<your_server>/users/payment-stripe/` - оплата курса авторизованным пользователем 
(POST-запрос с текстом: {"course":  <id_курса>}, Ответ включает ссылку на оплату сервиса stripe: "link": <ссылка>)  
`http://<your_server>/users/scheck-stripe-payments/` (POST-запрос) - проверка всех 
оплаченных через stripe курсов. Курсы в случае успешной оплаты вносятся в модель Payments (можно проверить в ендпоинте 
"payment/"). Ответ: статистика о количестве проверенных, оплаченных и ошибочных сессиях stripe. 

#### Подробная информация
Более подробную информацию о типах и json-содержмом запросов смотри на:
`http://<your_server>/swagger`
или
`http://<your_server>/redoc`

### Настройка сервера
1. Создайте Ваш сервер на базе Ubuntu, поддерживающем SSH протокол
2. Подключитесь к серверу командой в терминале  
`ssh <user_name>@<your_server_ip>`
3. Выполните обновления ПО на сервере по необходимости  
`sudo apt update && sudo apt upgrade`
4. Выполните настройку фаервола, оставив открытыми только порты 22, 80, 443
```commandline
sudo ufw status  
sudo ufw enable  # Если фаервол отключен
sudo ufw allow 80/tcp  
sudo ufw allow 443/tcp  
sudo ufw allow 22/tcp  
```

### Установка ПО на сервер (ручной деплой)
1. Создайте директорию где будет храниться проект командой `mkdir <directory>`
2. Перейдите в неё командой `cd <directory>`
3. Установите Docker по инструкции
https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository
4. Установите docker compose и pip:
```commandline
sudo apt update
sudo apt install docker-compose
sudo apt install git
sudo apt upgrade
```
5. Скопируйте репозиторий в текущую папку
`git clone -b develop --single-branch https://github.com/AleksandrG-dot/LMS-DRF.git`
6. Перейдите в паку LMS-DRF командой `cd LMS-DRF`
'cd LMS-DRF'
7. Создайте файл переменных окружения .env по примеру .env.example
'nano .env'
8. Запустите контейнеры. Произойдет скачивание на сервер всех необходимых образов. Затраченное время около 1-5 минут в зависимости от скорости интернет вашего сервера
`docker-compose up -d`
9. Проект настроен. Поздравляем с успешной настройкой.

### Настройки автоматичекого деплоя (обновления сервера автоматически)
Для настройки автоматического деплоя проекта на сервер укажите свои настройки секрета GitHub:
SECRET_KEY, DOCKER_HUB_ACCESS_TOKEN, DOCKER_HUB_USERNAME, SSH_KEY,SSH_USER, SERVER_IP, DOCKER_HUB_USERNAME, EMAIL_HOST, EMAIL_PORT  
И используйте файл ci.yml


### Структура сервисов
- web: Django приложение на порту 8000
- db: PostgreSQL база данных на порту 5432
- redis: Redis кэш на порту 6379
- celery: Celery worker для отложенных задач
- celery_beat: Celery beat для периодических задач


Продолжаем работать с проектом от ДЗ 34.1 и 34.2  
Здесь:  
- создана удаленная виртуальная машина (ВМ) на Yandex Cloud. На ней далее будет развернут сервер. Управление осуществляется по протоколу SSH
- получен новый ключ ssh rsa на локальной машине (папка .ssh) и привязан к ВМ
- настроена виртуальная машина на Yandex Cloud: обновление всех пакетов, установка Docker, Docker compose, pip, настройка фаервола
- в проект добавлен сервер Nginx, который запустится контейнером на ВМ согласно Dockerfile (nginx:latest): в docker-compose.yml и директория nginx с содержимым
- выполнена базовая настройка сервера Nginx в nginx.conf
- реализован пайплайн Django-приложения LMS-DRF:
- произведена настройка  CI/CD с помощью GitHub Actions и Docker Hub. Сценарий в .github/workflows/ci.yml
- Пункты ci.yml: проверка линтером flake8 -> запуск тестов в test.py -> сборка и отправка образа на DockerHub -> деплой образа с DockerHub на сервер. Ошибка на одном из пунктов приведет к остановке дальнейшего выполнения.
- создан аккаунт на Docker Hub
- прописаны переменные в секретах GitHub (ip-адрес сервера, ssh-ключ сервера, имя пользователя на сервере, имя пользователя DockerHub, токен DockerHub)



## Домашняя работа для уроков: 34.1 Docker и 34.2 Docker Compose
<details><summary>Подробности</summary>  

### Шаги для запуска всех сервисов

1. **Клонируйте репозиторий**
`git clone https://github.com/AleksandrG-dot/LMS-DRF/tree/develop`
2. **Настройте переменные окружения**
- Создайте файл .env в корне проекта
- Заполните его по примеру .env.example
3. **Запустите проект командой**  
`docker-compose up -d`  (дождитесь сборки и/или загрузки образов)  
Теперь можно использовать проект.  
Для входа в админку необходим суперпользователь, команда для создания суперпользователя приведена ниже.

### Полезные команды
- Создание суперпользователя (admin@skylearn.ru, pass: 123qwe): `docker-compose exec web python manage.py createadmin`
- Остановка всех сервисов: `docker-compose down`
- Пересборка образа: `docker-compose up -d --build`
- Выполнение миграций: `docker-compose exec web python manage.py migrate`
- Просмотр логов: `docker-compose logs <service_name>`.

### Проверка работоспособности сервисов
- Django (web): http://localhost:8000
- API документация: http://localhost:8000/swagger/ или http://localhost:8000/redoc/
- Admin Panel: http://localhost:8000/admin/
- PostgreSQL (db): проверяется автоматически через healthcheck
- Redis (redis): проверяется автоматически через healthcheck
- Celery Worker (celery): логи можно посмотреть через `docker-compose logs celery`
- Celery Beat (celery_beat): логи можно посмотреть через `docker-compose logs celery_beat`

### Структура сервисов
- web: Django приложение на порту 8000
- db: PostgreSQL база данных на порту 5432
- redis: Redis кэш на порту 6379
- celery: Celery worker для отложенных задач
- celery_beat: Celery beat для периодических задач


### URL-адреса  
http://127.0.0.1:8000/materials/course/ - курсы  
http://127.0.0.1:8000/materials/lesson/ - уроки  (id/, create/, id/delete/, id/update/)  
http://127.0.0.1:8000/users/ - пользователи (register/, login/, token/refresh/, list/, id/, id/update/, id/delete/)  
http://127.0.0.1:8000/users/payment/ - платежи  
http://127.0.0.1:8000/users/subs/ - управление подписками пользователей  
http://127.0.0.1:8000/users/payment-stripe/ - оплата курса авторизованным пользователем 
(POST-запрос с текстом: {"course":  <id_курса>}, Ответ включает ссылку на оплату сервиса stripe: "link": <ссылка>)  
http://127.0.0.1:8000/users/scheck-stripe-payments/ (POST-запрос) - проверка всех 
оплаченных через stripe курсов. Курсы в случае успешной оплаты вносятся в модель Payments (можно проверить в ендпоинте 
"payment/"). Ответ: статистика о количестве проверенных, оплаченных и ошибочных сессиях stripe. 

Продолжаем работать с проектом от ДЗ 33  
Здесь выполнена реализация многоконтейнерного приложения:  
- создан и заполнен файл Dockerfile для автоматического сбора Docker-образа
- добавлен файл с исключениями .dockerignore
- создан и заполнен файл docker-compose.yml автоматического сбора образов и запуска контейнеров
</details>


## Домашняя работа для урока: 33. Celery (Отложенные и периодические задачи)
<font color="green">Финальная работа по Django REST Framework</font>
<details><summary>Подробности</summary>

### Применить миграции
`python manage.py migrate`

### Наполнение данными
`python manage.py add_groups`  - добавление групп  
`python manage.py add_users`  - добавление пользователей (включая суперпользователя, пароль от всех - 123qwe)  
`python manage.py add_courses` - добавление курсов  
`python manage.py add_lessons`  - добавление уроков  
`python manage.py add_payments`  - добавление платежей  

### Создание суперпользователя
`python manage.py createadmin` - создание суперпользователя (admin@skylearn.ru, pass: 123qwe)

### URL-адреса  
http://127.0.0.1:8000/materials/course/ - курсы  
http://127.0.0.1:8000/materials/lesson/ - уроки  (id/, create/, id/delete/, id/update/)  
http://127.0.0.1:8000/users/ - пользователи (register/, login/, token/refresh/, list/, id/, id/update/, id/delete/)  
http://127.0.0.1:8000/users/payment/ - платежи  
http://127.0.0.1:8000/users/subs/ - управление подписками пользователей  
http://127.0.0.1:8000/users/payment-stripe/ - оплата курса авторизованным пользователем 
(POST-запрос с текстом: {"course":  <id_курса>}, Ответ включает ссылку на оплату сервиса stripe: "link": <ссылка>)  
http://127.0.0.1:8000/users/scheck-stripe-payments/ (POST-запрос) - проверка всех 
оплаченных через stripe курсов. Курсы в случае успешной оплаты вносятся в модель Payments (можно проверить в ендпоинте 
"payment/"). Ответ: статистика о количестве проверенных, оплаченных и ошибочных сессиях stripe. 

Продолжаем работать с проектом от ДЗ 32.2  
Здесь:  
- установка celery, redis, django-celery-beat
- реализована асинхронная отправка сообщений при обновлении курса пользователям, подписанным на него (модель Subscription)
с использованием отложенных задач (метод perform_update, метод task.py/send_information_about_update) 
- реализована фоновая периодическая задача materials\task.py\block_unused_user, которая делает неактивными 
(is_active=False) пользователей если дата последнего входа (last_login) больше чем 1 месяц. 
Настройки периодичности задачи установлены в параметре CELERY_BEAT_SCHEDULE настроек settings.py. 
Для проверки в фикстурах есть пользователь с email moderator_2@skylearn.ru.
</details>


## Домашняя работа для урока: 32.2 Документирование и безопасность (+ Интеграции)
<details><summary>Подробности</summary>  
Безопасность в этом уроке не настраивали.

### Применить миграции
`python manage.py migrate`

### Наполнение данными
`python manage.py add_groups`  - добавление групп  
`python manage.py add_users`  - добавление пользователей (включая суперпользователя, пароль от всех - 123qwe)  
`python manage.py add_courses` - добавление курсов  
`python manage.py add_lessons`  - добавление уроков  
`python manage.py add_payments`  - добавление платежей  

### Создание суперпользователя
`python manage.py createadmin` - создание суперпользователя (admin@skylearn.ru, pass: 123qwe)

### URL-адреса  
http://127.0.0.1:8000/materials/course/ - курсы  
http://127.0.0.1:8000/materials/lesson/ - уроки  (id/, create/, id/delete/, id/update/)  
http://127.0.0.1:8000/users/ - пользователи (register/, login/, token/refresh/, list/, id/, id/update/, id/delete/)  
http://127.0.0.1:8000/users/payment/ - платежи  
http://127.0.0.1:8000/users/subs/ - управление подписками пользователей  
http://127.0.0.1:8000/users/payment-stripe/ <font color="red">(новое)</font> - оплата курса авторизованным пользователем 
(POST-запрос с текстом: {"course":  <id_курса>}, Ответ включает ссылку на оплату сервиса stripe: "link": <ссылка>)  
http://127.0.0.1:8000/users/scheck-stripe-payments/ (POST-запрос) <font color="red">(новое)</font>- проверка всех 
оплаченных через stripe курсов. Курсы в случае успешной оплаты вносятся в модель Payments (можно проверить в ендпоинте 
"payment/"). Ответ: статистика о количестве проверенных, оплаченных и ошибочных сессиях stripe. 

Продолжаем работать с проектом от ДЗ 32.1  
Здесь:  
- реализовано документирование с использованием drf-yasg: установка, настройка в settings.py, настройка схемы и URL-ссылок, ручное документирование декораторами @method_decorator и @swagger_auto_schema
- добавлена библиотека stripe для работы с эквайрингом stripe.com
- ключ STRIPE_API_KEY вынесен в .env
- реализована новая модель users.PaymentCourseStripe для работы с платежами через Stripe
- добавлены поля price к моделям Course и Lesson
- Для обработки заказов добавлен эндпоинт "payment-stripe/", представление PaymentsCourseStripeCreateAPIView, сериалайзер PaymentCourseStripeSerializer.
- Логика работы с stripe.com вынесена в сервисный слой (файл serializer.py)  
<font color="red">Дополнительное задание (ниже)</font>
- реализована проверка статуса оплаты в stripe.
- в случае оплаты данные вносятся в модель Payment, меняется статус is_paid на True в модели PaymentCourseStripe.
- для этого реализованы эндпоинт "check-stripe-payments/", представление CheckStripePaymentStatusAPIView и сервисная функция check_stripe_payment
</details>


## Домашняя работа для урока: 32.1 Валидаторы, пагинация и тесты
<details><summary>Подробности</summary>  

### Применить миграции
`python manage.py migrate`

### Наполнение данными
`python manage.py add_courses` - добавление курсов  
`python manage.py add_lessons`  - добавление уроков  
`python manage.py add_users`  - добавление пользователей (включая суперпользователя, пароль от всех - 123qwe)  
`python manage.py add_groups`  - добавление групп  
`python manage.py add_payments`  - добавление платежей  

### Создание суперпользователя
`python manage.py createadmin` - создание суперпользователя (admin@skylearn.ru, pass: 123qwe)

### URL-адреса  
http://127.0.0.1:8000/materials/course/ - курсы  
http://127.0.0.1:8000/materials/lesson/ - уроки  (id/, create/, id/delete/, id/update/)  
http://127.0.0.1:8000/users/ - пользователи (register/, login/, token/refresh/, list/, id/, id/update/, id/delete/)  
http://127.0.0.1:8000/users/payment/ - платежи  
http://127.0.0.1:8000/users/subs/ - управление подписками пользователей (новое)

Продолжаем работать с проектом от ДЗ 31  
Здесь:  
- реализована функция-валидатор validate_url_youtube, проверяющий поле ссылки link_video на присутствие текста "youtube.com"
- реализована модель подписок Subscription в приложении user
- реализован контроллер SubscriptionAPIView для работы с Subscription
- реализован новый эндпоинт `/users/subs/` для работы с подписками (POST-запрос с телом запроса {"course": "<int>"})
- добавлено новое поле subscription (тип bool) при выборке данных по курсам, показывающее есть ли у текущего 
авторизованного пользователя подписка на обновление для курса (в сериализаторе CourseSerializer)
- добавлена пагинация для вывода курсов и уроков (CourseViewSet, LessonListApiView) с использованием кастомного 
пагинатора CustomPagination
- добавлено тестирование ендпоинтов на модель уроков Lesson. Проверка работы CRUD с различными правами доступа.
- добавлено тестирование функционала работы подписки на обновления (модель Subscription)
- добавлено тестирование ендпоинтов на модель курсов Course (конроллер viewsets.ModelViewSet)
- установлен пакет coverage для подсчета покрытия тестами
- сгенерированы отчеты по проверке покрытия тестами (coverage.txt, \htmlcov_DZ32.1)  
</details>



## Домашняя работа для урока: 31 Права доступа в DRF
<details><summary>Подробности</summary>  

### Применить миграции
`python manage.py migrate`

### Наполнение данными
`python manage.py add_courses` - добавление курсов  
`python manage.py add_lessons`  - добавление уроков  
`python manage.py add_users`  - добавление пользователей (включая суперпользователя, пароль от всех - 123qwe)  
`python manage.py add_groups`  - добавление групп  
`python manage.py add_payments`  - добавление платежей  

### Создание суперпользователя
`python manage.py createadmin` - создание суперпользователя (admin@skylearn.ru, pass: 123qwe)

### URL-адреса  
http://127.0.0.1:8000/materials/course/ - курсы  
http://127.0.0.1:8000/materials/lesson/ - уроки  (id/, create/, id/delete/, id/update/)  
http://127.0.0.1:8000/users/ - пользователи (register/, login/, token/refresh/, list/, id/, id/update/, id/delete/)  
http://127.0.0.1:8000/users/payment/ - платежи

Продолжаем работать с проектом от ДЗ 30.2  
Здесь:  
- установлен djangorestframework-simplejwt и настроена JWT-авторизация
- переделан CRUD для пользователей с использованием generic (в том числе регистрация пользователей)
- настроено в проекте использование JWT-авторизации
- закрыт каждый эндпоинт авторизацией (IsAuthenticated, в settings.py)
- эндпоинты для регистрации ("register/") и авторизации ("login/") открыты для неавторизованных пользователей
- добавлена кастомная команда для создания суперпользователя
- добавлена группа модераторов "moders", фикстуры к ней и кастомная команда для заполнения
- добавлен класс IsModer (\users\permissions.py) для проверки принадлежности пользователя к группе модераторов
- изменены права доступа: модераторы могут просматривать и редактировать любые курсы и уроки, но не могут их удалять и создавать
- обновлены фикстуры пользователей
- внесены новые поля владельцев (owner) в модели Course и Lesson
- добавлен класс IsOwner (\users\permissions.py) для проверки текущего пользователя на предмет владения объектом.
- изменены права доступа: пользователи-немодераторы могут просматривать, редактировать и удалять только свои курсы и уроки, могут создавать новые
- обновлены фикстуры курсов и уроков
</details>

## Домашняя работа для урока: 30.2 Сериализаторы
<details><summary>Подробности</summary>  

### Применить миграции
`python manage.py migrate`

### Наполнение данными
`python manage.py add_courses` - добавление курсов  
`python manage.py add_lessons`  - добавление уроков  
`python manage.py add_users`  - добавление пользователей \* (пароль от всех - 123qwe)  
`python manage.py add_payments`  - добавление платежей  

### URL-адреса  
http://127.0.0.1:8000/materials/course/ - курсы  
http://127.0.0.1:8000/materials/lesson/ - уроки  
http://127.0.0.1:8000/users/user/ - пользователи \*  
http://127.0.0.1:8000/users/payment/ - платежи

Продолжаем работать с проектом от ДЗ 30.1  
Здесь:
- добавлен вывод количества уроков в курсе "lesson_count" (изменен CourseSerializer, с использованием SerializerMethodField())
- добавлены эндпоинты для редактирования пользователей (User) на основе ViewSet
- добавлена модель платежей (Payment) в приложении users
- добавлены эндпоинты к модели платежей (Payment) на основе ViewSet
- созданы фикстуры для моделей курсов, уроков, пользователей и платежей. Добавлены кастомные команды для их загрузки.
- \* Пароль от пользователей хранится без хеширования в текстовом поле, т.к. пользователи созданы через API интерфейс. Сокрытия паролей еще не проходили.  
- добавлен список всех уроков курса для сериализатора модели курсов (2 вариант)
- добавлена возможность сортировать списка платежей по дате. Например, http://127.0.0.1:8000/users/payment?ordering=-date
- добавлена возможность фильтровать списка платежей по курсу, уроку и способу оплаты. Например, http://127.0.0.1:8000/users/payment?course=1  
</details>