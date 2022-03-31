## Запуск сервиса

_Все команды в терминале выполняются в каталоге UGC-service/admin-panel._

1. Переименовать .env.sample в .env.dev
2. Уточнить при необходимости параметры подключения к базе данных (имя пользователя, пароль)
3. Запустить docker-compose командой:
```shell
docker-compose up --build -d
```
4. Подключиться к postgresql командой:
```shell
docker exec -it admin-panel-db-1 psql -U django_user -t movies_database
```
5. Создать схему `content` командой:
```postgresql
CREATE SCHEMA content;
```
6. Отключиться от postgresql - `exit`
7. Выполнить миграции django:
```shell
docker exec -it admin-panel-web-1 python manage.py migrate
```
8. Создать суперпользователя для подключения к админке django
```shell
docker exec -it admin-panel-web-1 python manage.py createsuperuser
```
9. Заполнить бд данными. Для этого выполнить скрипт:
```shell
python ./sqlite_to_postgres/sqlite_to_posgres.py
```

10. Админка доступна по адресу: 
```http request
http://127.0.0.1:8000/admin
```