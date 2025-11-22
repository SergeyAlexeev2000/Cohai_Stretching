# Cohai Stretching – Backend Plan
Последнее обновление: 2025-11-19

---

# Шаг 1 — Инфраструктура проекта

**Цель:** стабильная база проекта, venv, структура каталогов, логирование.

## 1.1. Среда разработки
- Создание `venv`, `requirements.txt`.
- Базовая структура:
  - `app/main.py`
  - `app/core/*` (config, logging, exceptions)
  - `app/db/*` (session, base)
  - `app/models/*`
  - `app/repositories/*`
  - `app/services/*`
  - `app/api/v1/*`
  - `app/tools/*`
  - `app/logs/app.log`

## 1.2. Логирование и глобальная обработка ошибок
- `app/core/logging.py`
- `app/core/exceptions.py`
- Глобальный обработчик ошибок
- Тестовый эндпоинт `/api/v1/test-error`

**Статус шага 1:** завершено.

---

# Шаг 2 — База данных и модели

**Цель:** корректные SQLAlchemy-модели и полностью рабочая SQLite-БД.**

## 2.1. Модели SQLAlchemy
- `Location`
- `ProgramType`
- `Trainer`
- `MembershipPlan`
- `ClassSession`

### Связи:
- Location 1–N MembershipPlan  
- Location 1–N ClassSession  
- ProgramType 1–N ClassSession  
- Trainer 1–N ClassSession  
- MembershipPlan 1–N ClassSession (опциональная FK)

## 2.2. Скрипты обслуживания
- `check_sqlalchemy.py` — проверяет мапперы
- `bootstrap_db.py` — создаёт таблицы и тестовые данные

**Статус шага 2:** завершено.

---

# Шаг 3 — Репозитории и сервисы

**Цель:** разделение данных (репозитории) и логики (сервисы).**

## 3.1. Репозитории
- `location_repo.py`
- `program_type_repo.py`
- `membership_repo.py`
- `trainer_repo.py`
- `class_session_repo.py`
- `lead_repo.py`

Каждый репозиторий содержит:
- list()
- list_by_location()
- get_by_id()
- create()
- update()
- delete()

## 3.2. Сервисы
- `schedule_service.py`
- `membership_service.py`
- `lead_service.py`

**Статус шага 3:** в процессе.

---

# Шаг 4 — Публичное API

**Цель:** REST-слой для фронтенда.**

Файл: `app/api/v1/public.py`

## 4.1. Уже работает
- `GET /api/v1/locations`
- `GET /api/v1/program-types`
- `GET /api/v1/schedule?location_id=…`

## 4.2. Нужно завершить
- `GET /api/v1/memberships`
- `GET /api/v1/memberships/{id}`
- фильтрация по location_id
- валидация входных параметров

## 4.3. Тесты (pytest)
- тест `/memberships`
- тест несуществующего id
- тест несуществующей локации

**Статус шага 4:** завершено (после фикса membership API + pytest).

---

# Шаг 5 — Админское API (CRM для лидов) (мы сейчас здесь)

Файл: `app/api/v1/admin_leads.py`

## 5.1. Основные эндпоинты
- `GET /api/v1/admin/leads`
- `GET /api/v1/admin/leads/{id}`
- `POST /api/v1/admin/leads`
- `PATCH /api/v1/admin/leads/{id}`

## 5.2. Схемы
Файл: `app/schemas/lead.py`
- LeadBase
- LeadCreate
- LeadRead
- LeadUpdate

## 5.3. Авторизация
Начать можно без авторизации или с простым ключом.

**Статус шага 5:** запланировано.

---

# Шаг 6 — Фронт и интеграция

## 6.1. Mock-фронт
- Swagger UI
- Postman коллекция

## 6.2. Настоящий фронтенд
- Репозиторий: `cohai_frontend`
- Просмотр:
  - локации
  - расписание
  - форма заявки (lead)

**Статус шага 6:** запланировано.

---

# Шаг 7 — Деплой

## 7.1. Dev-деплой
- Dockerfile
- docker-compose
- run uvicorn/gunicorn в контейнере

## 7.2. Прод-деплой
- VPS / Render / Fly.io
- Настройки для продакшена:
  - логирование
  - health-check
  - мониторинг

**Статус шага 7:** запланировано.

---

# Шаг 8 — Будущее развитие
- Новый функционал
- Оптимизации
- Логи бизнес-событий
- Интеграции (CRM/Telegram)

**Статус шага 8:** на будущее.
