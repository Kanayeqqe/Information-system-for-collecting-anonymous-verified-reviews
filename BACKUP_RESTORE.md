# Backup and Restore Automation

В этом проекте реализованы автоматические скрипты для резервного копирования базы данных PostgreSQL и медиа-файлов, а также для полного восстановления системы из бэкапа.

## Файлы

- `scripts/backup.sh` — создает:
  - SQL-дамп базы данных с уникальным именем `backups/db_backup_<timestamp>.sql`
  - архив медиа-файлов `uploads` в `backups/uploads_backup_<timestamp>.tar.gz`
- `scripts/restore.sh` — восстанавливает данные из последнего доступного бэкапа или из указанных файлов
- `uploads/.gitkeep` — пустой файл, чтобы папка `uploads` присутствовала в репозитории

## Использование

### 1. Подготовка

1. Скопируйте `.env.example` в `.env`.
2. Заполните значения:
   - `DB_HOST`
   - `DB_PORT`
   - `DB_NAME`
   - `DB_USER`
   - `DB_PASSWORD`

### 2. Создание бэкапа

```bash
bash scripts/backup.sh
```

В результате в папке `backups/` появятся файлы:
- `db_backup_YYYYMMDD_HHMMSS.sql`
- `uploads_backup_YYYYMMDD_HHMMSS.tar.gz`

### 3. Восстановление системы

```bash
bash scripts/restore.sh
```

Если хотите восстановить определенный бэкап:

```bash
bash scripts/restore.sh backups/db_backup_2026_06_15_123456.sql backups/uploads_backup_2026_06_15_123456.tar.gz
```

## Особенности

- Скрипты читают параметры подключения из `.env`, пароли не зашиты в код.
- В режиме Docker, если сервис `db` доступен, используется `docker compose exec db`.
- Бэкап SQL создается с опцией `--clean --if-exists`, чтобы восстановление могло выполняться на чистой или существующей базе.
- Резервируются медиа-файлы из директории `uploads/`.

## Проверка работоспособности

1. Запустите приложение.
2. Создайте тестовые данные через интерфейс или API.
3. Выполните `bash scripts/backup.sh`.
4. Убедитесь, что `backups/` содержит файлы бэкапа.
5. Удалите содержимое базы данных и папку `uploads/`.
6. Выполните `bash scripts/restore.sh`.
7. Проверьте, что данные и файлы восстановлены.
