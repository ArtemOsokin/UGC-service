## Запуск сервиса event-api (UGC-service)

_Все команды в терминале выполняются в каталоге UGC-service/event-api._

1. Переименовать файл .env.sample в .env для dev (переменная SETTINGS=dev). 
Изменить при необходимости значения переменных окружения (необязательно).
2. Поднять проект в docker-compose:
```shell
docker-compose up --build -d
```
3. Документация openapi сервера доступна по адресу:
```http request
http://127.0.0.1/api/openapi
```
4. Для авторизации в документации openapi или при отправке запросов на ручки сервиса использовать валидный access-token, полученный 
в сервисе auth-api или использовать нижеуказанный access-токен (продленный срок действия):
`eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY0OTAwOTcyNCwianRpIjoiZjk5OGFmYzItZDQxMC00YzBiLThlODUtOGZmNmU4M2I1ZDdiIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImFkZTgzNWEyLWMwZTQtNGU4My1hMDE2LTRmMjZmYjMxOWY5NSIsIm5iZiI6MTY0OTAwOTcyNCwiZXhwIjoxNjQ5NjE0NTI0LCJpc19hZG1pbiI6ZmFsc2UsImlzX3N0YWZmIjpmYWxzZSwicm9sZXMiOlsiZ3Vlc3QiXX0.TCoOawM_1_VitmmCLPhqWLJzm6AbNXQzhQeTW8Bl_pc`
5. Control center KAFKA доступен по адресу:
```http request
http://127.0.0.1:9021/clusters
```
6. JAEGER UI доступен по адресу:
```http request
http://127.0.0.1:16686/search
```
