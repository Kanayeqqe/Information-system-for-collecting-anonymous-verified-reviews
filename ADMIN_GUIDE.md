# Руководство администратора

## Цель

Это руководство описывает развертывание, эксплуатацию и восстановление проекта Anonymous Verified Reviews System.

## Содержание
- Быстрое развертывание
- Конфигурация Nginx
- Проверка состояния
- Восстановление после сбоев
- Рекомендации по безопасности

---

## 1. Быстрое развертывание

### 1.1 Требования к серверу

- Операционная система: Linux (Ubuntu 22.04+, Debian 12+, CentOS 9+)
- Минимум: 2 vCPU, 4 ГБ RAM
- Рекомендуется: 4 vCPU, 8 ГБ RAM
- Место на диске: минимум 20 ГБ свободного пространства
- Сеть: открыты порты `80`, `443`, `8000`, `5173`

### 1.2 Подготовка

1. Склонируйте репозиторий и перейдите в папку проекта:
   ```bash
git clone https://github.com/Kanayeqqe/Information-system-for-collecting-anonymous-verified-reviews.git
cd Information-system-for-collecting-anonymous-verified-reviews
```
2. Создайте файл `.env` на основе `.env.example`.
3. Убедитесь, что переменные окружения заполнены.

### 1.3 Запуск с Docker

```bash
docker compose up -d --build
```

### 1.3 Проверка

- Backend: `http://localhost:8000/health`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Frontend: `http://localhost:5173`

---

## 2. Конфигурация веб-сервера (Reverse Proxy)

### 2.1 Общие принципы

Для распределения входящего сетевого трафика, сокрытия внутренней архитектуры портов бэкенда и обеспечения безопасного соединения используется обратный прокси-сервер Nginx.

- Backend API доступен на `http://localhost:8000`.
- Frontend запущен на `http://localhost:5173`.
- Nginx принимает входящие запросы и проксирует их к нужному сервису.
- Этот проект совместим с Nginx как reverse proxy.

### 2.2 Листинг конфигурационного файла веб-сервера

```nginx
server {
    listen 80;
    server_name reviews.example.com;

    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }

    location /redoc {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        rewrite ^/api(/.*)$ $1 break;
    }

    location / {
        proxy_pass http://127.0.0.1:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
```

> Примечание: если вы не используете префикс `/api/`, настройка `rewrite` можно исключить.

### 2.3 План аварийного восстановления системы (Disaster Recovery)

#### Инцидент 1: Нарушение связности с СУБД

Алгоритм действий:
1. Проверить статус контейнера БД:
   ```bash
docker compose ps db
```
2. Проверить доступность базы данных:
   ```bash
docker compose exec db pg_isready -U "$DB_USER" -d "$DB_NAME"
```
3. Просмотреть логи PostgreSQL for причины ошибки:
   ```bash
docker compose logs db
```
4. Если БД не отвечает, перезапустить контейнер:
   ```bash
docker compose restart db
```
5. При необходимости восстановить схему из `db/schema.sql`:
   ```bash
docker compose exec db psql -U "$DB_USER" -d "$DB_NAME" -f /docker-entrypoint-initdb.d/01-schema.sql
```
6. Если база повреждена и требуется полное восстановление, используйте резервные копии или пересоздайте контейнер при сохранении данных.

#### Инцидент 2: Критический программный сбой основного процесса бэкенда

Алгоритм действий:
1. Проверить статус контейнера API:
   ```bash
docker compose ps api
```
2. Просмотреть последние логи сервиса:
   ```bash
docker compose logs -f api
```
3. Перезапустить сервис:
   ```bash
docker compose restart api
```
4. Проверить эндпоинт здоровья:
   ```bash
curl http://localhost:8000/health
```
5. Если перезапуск не помог, проверить ошибки зависимостей и доступ к БД.
6. При необходимости откатить последнюю версию кода или пересобрать контейнер:
   ```bash
docker compose build api
docker compose up -d api
```

---

## 3. Проверка состояния

### 3.1 Статус Docker

```bash
docker compose ps
```

### 3.2 Просмотр логов

```bash
docker compose logs -f api
```

### 3.3 Тестирование API

```bash
curl http://localhost:8000/health
```

### 3.4 Веб-интерфейс

Откройте `http://localhost:5173` и проверьте, что приложение запускается.

---

## 4. Восстановление после сбоев

### 4.1 Перезапуск сервисов

```bash
docker compose restart api db bot frontend
```

### 4.2 Если контейнеры не стартуют

1. Посмотрите логи:
   ```bash
docker compose logs api
```
2. Проверьте доступ к базе данных:
   ```bash
docker compose exec db pg_isready -U $DB_USER -d $DB_NAME
```

### 4.3 Если диск заполнен

1. Освободите место, удалив ненужные Docker-ресурсы:
   ```bash
docker system prune -af
```
2. Если логи занимают много места, очистите их:
   ```bash
truncate -s 0 $(docker inspect --format='{{.LogPath}}' $(docker ps -aq))
```
3. Проверьте свободное место:
   ```bash
df -h
```

### 4.4 Восстановление базы данных

Если база данных повреждена или требует пересоздания:

```bash
docker compose down
rm -rf ./db_data
docker compose up -d --build
```

Для ручного восстановления структуры через PostgreSQL:

```bash
docker compose exec db psql -U <DB_USER> -d <DB_NAME> -f /docker-entrypoint-initdb.d/01-schema.sql
```

### 4.4 Восстановление данных из seed-файла

Файл `db/seed.sql` предоставлен для начальной загрузки.
Если необходимо повторно инициализировать данные, выполните:

```bash
docker compose exec db psql -U <DB_USER> -d <DB_NAME> -f /docker-entrypoint-initdb.d/02-seed.sql
```

---

## 5. Рекомендации по безопасности

- Никогда не храните `.env` в публичных репозиториях.
- Используйте сложные, уникальные пароли для PostgreSQL.
- При разворачивании в production включите HTTPS на уровне Nginx.
- Если бот не запускается, проверьте `TELEGRAM_BOT_TOKEN`.

---

## 6. Контрольные точки эксплуатации

- API: `http://localhost:8000/health`
- Swagger: `http://localhost:8000/docs`
- Frontend: `http://localhost:5173`
- OpenAPI: `http://localhost:8000/openapi.json`

---

## 7. Частые ошибки

### 7.1 Ошибка подключения к БД

Убедитесь, что переменные `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` заданы правильно.

### 7.2 Ошибка 404 на `/box/{uuid}`

Проверьте, что `uuid` существует и вы передали корректный `token`.

### 7.3 Ошибка 401/403 на `/auth` или `/box/{uuid}`

Проверьте формат заголовка `Authorization` и значение `owner_token`.

---

## 8. Сервисные команды

### Пересборка контейнера API

```bash
docker compose build api
```

### Принудительное удаление и пересоздание

```bash
docker compose down --volumes
docker compose up --build -d
```
