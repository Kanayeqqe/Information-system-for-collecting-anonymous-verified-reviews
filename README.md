# Anonymous Verified Reviews System

> Сервис для сбора анонимных, верифицированных отзывов с безопасным доступом владельца.

## 📖 О проекте
Anonymous Verified Reviews System позволяет собирать анонимные отзывы, управлять ими из защищенного ящика (`box`) и отвечать на сообщения владельцем.

### Что делает система
- Принимает анонимные отзывы в заданный `box`.
- Обеспечивает доступ владельцу через `owner_token`.
- Позволяет владельцу отвечать на отзывы без раскрытия автора.
- Поддерживает регистрацию / авторизацию владельцев через токен.
- Содержит автоматическую документацию OpenAPI.

---

## 📁 Структура проекта
```text
.
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── api/openapi.yaml
├── db/schema.sql
├── db/seed.sql
├── README.md
├── ADMIN_GUIDE.md
├── pyproject.toml
├── requirements.txt
├── src/
│   ├── main.py
│   ├── core/
│   ├── db/
│   ├── middlewares/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   └── utils/
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── public/
    └── src/
```

> Основной backend расположен в `src/`, а SQL-схема и миграционные файлы — в `db/`.

---

## 🛠 Технологический стек

### Backend
- Python 3.11
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

### Frontend
- React
- Vite
- Tailwind CSS
- Electron

### Инфраструктура
- Docker
- Docker Compose
- PostgreSQL
- OpenAPI / Swagger / ReDoc

---

## 🚀 Требования
- Docker Desktop
- Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL (для локального запуска без Docker)

---

## 🌐 Переменные окружения

Файл конфигурации: `.env`

Используйте `.env.example` как шаблон.

### Рекомендуемая конфигурация
```env
DB_HOST=db
DB_PORT=5432
DB_NAME=avr_db
DB_USER=avr_user
DB_PASSWORD=strong_password_here

TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
API_BASE_URL=http://localhost:8000
PUBLIC_API_BASE_URL=http://localhost:8000
```

### Описание переменных
Таблица показывает, где используется каждая переменная.

| Переменная | Значение | Используется в | Описание |
| --- | --- | --- | --- |
| `DB_HOST` | `db` | backend, bot | Хост PostgreSQL внутри Docker Compose или `localhost` для локального запуска |
| `DB_PORT` | `5432` | backend, bot | Порт PostgreSQL |
| `DB_NAME` | `avr_db` | backend, bot | Имя базы данных |
| `DB_USER` | `avr_user` | backend, bot | Пользователь PostgreSQL |
| `DB_PASSWORD` | `strong_password_here` | backend, bot | Пароль PostgreSQL |
| `TELEGRAM_BOT_TOKEN` | `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` | bot | Токен Telegram-бота |
| `API_BASE_URL` | `http://localhost:8000` | bot, frontend | Базовый URL API для сервисов |
| `PUBLIC_API_BASE_URL` | `http://localhost:8000` | bot | Внешний доступный URL API |

> Примечание: `VITE_API_BASE_URL` настраивается в `frontend/.env.example` и используется только для frontend сборки.

---

## 🧰 Локальный запуск без Docker

### Backend
1. Создайте виртуальное окружение:
   ```bash
   python -m venv .venv
   ```
2. Активируйте его:
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - macOS / Linux:
     ```bash
     source .venv/bin/activate
     ```
3. Установите зависимости:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Создайте `.env` на основе `.env.example`.
5. Запустите backend:
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend
1. Перейдите в каталог frontend:
   ```bash
   cd frontend
   ```
2. Установите зависимости:
   ```bash
   npm install
   ```
3. Запустите frontend:
   ```bash
   npm run dev
   ```

> Фронтенд доступен по умолчанию на `http://localhost:5173`.

---

## 🐳 Установка Docker
# Скачайте Docker Desktop с официального сайта:
# https://www.docker.com/products/docker-desktop

# Или через winget (Windows 10/11)
```bash
winget install Docker.DockerDesktop
```

## 🐳 Запуск через Docker

### Запуск
```bash
docker compose up --build
```

### Запуск в фоне
```bash
docker compose up -d --build
```

### Остановка
```bash
docker compose down
```

### Проверка статуса
```bash
docker compose ps
```

### Перезапуск сервиса
```bash
docker compose restart api db bot frontend
```

---

## 📚 OpenAPI и интерактивная документация

После запуска backend доступны:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

Статический OpenAPI-файл: `api/openapi.yaml`.

---

## 📡 API endpoints

### Health
`GET /health`

Ответ:
```json
{
  "status": "ok"
}
```

### Создать новый box
`POST /box`

Заголовок:
```http
Authorization: Bearer <token>
```
(необязательно)

Ответ:
```json
{
  "uuid": "3f8b2d0f-1eae-4d99-a29b-9c2dbd02d0a3",
  "owner_token": "owner_1a2b3c4d5e"
}
```

### Отправить отзыв
`POST /box/{uuid}/feedback`

Тело запроса:
```json
{
  "text": "Это анонимный отзыв"
}
```

Удачный ответ:
```json
{
  "id": 1,
  "text": "Это анонимный отзыв",
  "status": "approved",
  "moderation_notes": null,
  "created_at": "2026-06-09T12:00:00",
  "replies": []
}
```

### Получить отзывы владельца
`GET /box/{uuid}`

Параметры:
- `token` — owner token в query
- `X-Owner-Token` — owner token в заголовке

Удачный ответ:
```json
{
  "uuid": "3f8b2d0f-1eae-4d99-a29b-9c2dbd02d0a3",
  "feedbacks": [
    {
      "id": 1,
      "text": "Это отзыв",
      "status": "approved",
      "moderation_notes": null,
      "created_at": "2026-06-09T12:00:00",
      "replies": []
    }
  ]
}
```

### Ответить на отзыв
`POST /feedback/{id}/reply`

Параметры авторизации:
- `token` в query
- `X-Owner-Token` в заголовке

Тело запроса:
```json
{
  "text": "Спасибо за ваш отзыв!"
}
```

Удачный ответ:
```json
{
  "id": 1,
  "text": "Спасибо за ваш отзыв!",
  "created_at": "2026-06-09T12:05:00"
}
```

### Регистрация владельца
`POST /auth/register`

Тело запроса:
```json
{
  "username": "admin",
  "password": "strong_password",
  "confirm_password": "strong_password"
}
```

Удачный ответ:
```json
{
  "username": "admin",
  "token": "owner-auth-token"
}
```

### Вход владельца
`POST /auth/login`

Тело запроса:
```json
{
  "username": "admin",
  "password": "strong_password"
}
```

Удачный ответ:
```json
{
  "username": "admin",
  "token": "owner-auth-token"
}
```

### Текущий пользователь
`GET /auth/me`

Заголовок:
```http
Authorization: Bearer owner-auth-token
```

### Список box текущего пользователя
`GET /auth/my-boxes`

### Список всех отзывов пользователя
`GET /auth/my-feedbacks`

---

## ⚠️ Коды ошибок
- `400 Bad Request` — неверная структура запроса или недопустимые данные.
- `401 Unauthorized` — отсутствует или неверен токен авторизации.
- `403 Forbidden` — нет доступа по owner token.
- `404 Not Found` — объект не найден.
- `429 Too Many Requests` — превышено ограничение частоты.
- `500 Internal Server Error` — внутренняя ошибка сервера.

---

## 🧪 Тестирование
Запустить unit-тесты:
```bash
pytest tests
```

---

## ℹ️ Дополнительная информация
- `docker-compose.yml` запускает сервисы `db`, `api`, `bot`, `frontend`.
- `db/schema.sql` содержит структуру таблиц PostgreSQL.
- `db/seed.sql` используется для начального наполнения данных.
- В frontend используется `VITE_API_BASE_URL` для связи с API.
- Интерактивная документация генерируется FastAPI на `/docs` и `/redoc`.

---
# 🧪 Тестирование
Backend:
```bash
pytest
```
Frontend:
```bash
npm test
```
---
# 📈 Возможные направления развития
- Telegram-уведомления о новых отзывах
- Email-уведомления
- Модерация сообщений
- Реакции на ответы
- Категории отзывов
- Аналитика и статистика
- Dashboard владельца
- JWT-аутентификация
- Поддержка нескольких владельцев
- Экспорт данных
---
# 🤝 Команда
## Team Lead
**Руслан Огнев**
- архитектура системы
- безопасность
- middleware
## Backend/fullstack
**Илья Жабенко**
- проектирование БД
- API
- бизнес-логика
## Frontend
**Александр Брягиня**
- UI/UX
- интеграция с API
## Frontend - bot
**Егор Лесовский**
- bot-разработка
- интеграция компонентов
---
# 🤝 Contributing
1. Fork репозитория
2. Создайте ветку
```bash
git checkout -b feature/new-feature
```
3. Внесите изменения
4. Создайте Pull Request
---
# 📄 License
Проект распространяется под лицензией, указанной в репозитории.
Если лицензия ещё не добавлена, рекомендуется использовать:
```text
MIT License
```
---
# ⭐ Цель проекта
Создать удобную платформу для получения честной и безопасной обратной связи, где пользователь может свободно выражать мнение, а владелец — получать структурированные отзывы без нарушения приватности отправителей.
