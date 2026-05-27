# Information-system-for-collecting-anonymous-verified-reviews

## 🚀Идея

Сервис для получения контролируемой обратной связи. Основной акцент сделан на анонимности отправителя при сохранении прозрачности для получателя.

---
## 👥 Команда

## 🔹Backend — Жабенко Илья

* модели БД
* API
* бизнес-логика

## 🔹Team Lead — Огнев Руслан

* архитектура
* безопасность
* middleware

## 🔹Frontend — Брягиня Александр 

* UI/UX
* работа с API

## 🔹FullStack — Лесовский Егор

---

## 🧩 Архитектура

```mermaid
flowchart LR

A[Анонимный пользователь] -->|POST feedback| B[Backend]

C[Владелец] -->|GET box| B
C -->|POST reply| B

B --> D[(Database)]

subgraph Backend
    B1[Controllers]
    B2[Services]
    B3[Middleware]
end

B --> B1
B1 --> B2
B2 --> D
B3 --> B1
```

### 📦 Основные сущности

- **Box** — ящик отзывов  

- **Feedback** — анонимный отзыв  

- **Reply** — ответ владельца  

---

## 🗄️ Структура базы данных!

[<img width="1266" height="764" alt="Untitled" src="https://github.com/user-attachments/assets/74fd666b-dd32-40cb-a98f-de89cbbb5b40" />](https://dbdiagram.io/d/69fa66b654a51d93d39c2be2)



---

## 🌎API

## Как использовать

- Импортируйте `openapi.yaml` в Swagger Editor, Postman или Insomnia.
- Разработчики backend должны реализовать API согласно спецификации.
- Перед запуском заполните `.env` с `TELEGRAM_BOT_TOKEN` и `API_BASE_URL`.
- Запустите локально с Docker: `docker compose up --build`.
- Откройте документацию API по адресу: `http://localhost:8000/docs` или `http://localhost:8000/redoc`.

## Первоначальная установка и запуск

1. Установите систему:
   - Docker Desktop для Windows.
   - Node.js.
   - Python.

2. Клонируйте репозиторий и перейдите в папку проекта:
   ```bash
   git clone <repo-url>
   cd Information-system-for-collecting-anonymous-verified-reviews
   ```

3. Подготовьте переменные окружения:
   - Создайте файл `.env` в корне проекта.
   - Добавьте в него:
     ```env
     TELEGRAM_BOT_TOKEN=ваш_токен
     API_BASE_URL=http://localhost:8000
     ```

4. Установите зависимости backend (если используете локальный запуск без Docker):
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Установите зависимости frontend:
   ```bash
   cd frontend
   npm install
   ```

6. Запустите приложение в Docker (рекомендуемый способ):
   ```bash
   docker compose up --build
   ```

7. Если вы предпочитаете запускать сервисы локально по отдельности:
   - Backend:
     ```bash
     uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
     ```
   - Frontend:
     ```bash
     cd frontend
     npm run dev
     ```

8. Откройте в браузере:
   - Backend: `http://localhost:8000`
   - Frontend: адрес, указанный в `npm run dev`

## Возможности

- Анонимная отправка отзывов
- Доступ только владельцу через токен
- Ответы на отзывы
- Токен можно передавать как параметр запроса `?token=...` или заголовок `X-Owner-Token`
- Базовая валидация и ограничение скорости

## Базовый URL

http://localhost:8000

---

## 📌 Отправить отзыв (аноним)

POST /box/{uuid}/feedback

`
{
  "text": "Ваш отзыв"
}`

## 📌 Получить отзывы (владелец)

GET /box/{uuid}?token=...

## 📌 Ответить на отзыв

POST /feedback/{id}/reply?token=...

---

## 🔐 Безопасность

## ✅ Анонимность

* IP не сохраняется (или хэшируется)
* user-agent — опционально

## ✅ Ограничение скорости

* 5–10 запросов / минута на IP
* применяется к:
    * POST /box/{uuid}/feedback

## ✅ Фильтрация текста

* максимум 500 символов
* blacklist слов
* удаление ссылок (regex)

## ✅ Авторизация

* доступ только при совпадении owner_token
