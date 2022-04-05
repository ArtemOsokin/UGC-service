## Запуск сервиса event-api (UGC-service) c KAFKA локально

_Все команды в терминале выполняются в каталоге UGC-service/event-api._

1. Переименовать файл .env.sample в .env для dev (переменная SETTINGS=dev). 
Изменить при необходимости значения переменных окружения (необязательно).
2. Установить значение переменной окружения `KAFKA_RUN_IN_YANDEX_CLOUD=False`
3. Поднять проект в docker-compose:
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

## Запуск сервиса event-api (UGC-service) с кластером KAFKA в Яндекc.Облако

1. Установить значение KAFKA_RUN_IN_YANDEX_CLOUD=True в файле .env
2. Поднять проект в docker-compose:
```shell
docker-compose -f docker-compose-yc.yaml up --build -d
```
3. Документация openapi сервера доступна по адресу:
```http request
http://127.0.0.1/api/openapi
```
4. Параметры Consumer для чтения топиков из кластера KAFKA:
```python
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'films_bookmarks',  # Имя топика для чтения
    bootstrap_servers='rc1b-dt0p7ntrbdum3iqb.mdb.yandexcloud.net:9091',  # FQDN хоста-брокера
    security_protocol="SASL_SSL",
    sasl_mechanism="SCRAM-SHA-512",
    sasl_plain_password='kafka_consumer42#',  # Пароль для Consumer
    sasl_plain_username='kafka_consumer',  # Имя роли с правами на чтение топиков
    ssl_cafile="C:/Users/User/.kafka/YandexCA.crt")  # Путь к сертификату SSL

print("ready")

for msg in consumer:
    print(msg.key.decode("utf-8") + ":" + msg.value.decode("utf-8"))
```
Приведенный скрипт после запуска будет непрерывно считывать новые сообщения из заданного топика и печатать их в консоль.
5. На кластере KAFKA настроены следующие топики:
- films_bookmarks, 2 partition
- films_feedbacks, 2 partition
- films_progress, 2 partition
6. Получить SSL сертификат для подключения к KAFKA из скриптов или IDE можно следующим образом:
```shell
для Linux(Bash)
sudo mkdir -p /usr/local/share/ca-certificates/Yandex && \
sudo wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" -O /usr/local/share/ca-certificates/Yandex/YandexCA.crt && \
sudo chmod 655 /usr/local/share/ca-certificates/Yandex/YandexCA.crt

для Windows(PowerShell)
mkdir $HOME\.kafka; curl.exe -o $HOME\.kafka\YandexCA.crt https://storage.yandexcloud.net/cloud-certs/CA.pem
```
Cертификат YandexCA.crt будет расположен директории:

`/usr/local/share/ca-certificates/Yandex/` для Ubuntu;
`$HOME\.kafka\` для Windows.

В контейнере сервиса event-api сертификат скачивается при создании контейнера и располагается по пути:
`/usr/local/share/ca-certificates/Yandex/YandexCA.crt`