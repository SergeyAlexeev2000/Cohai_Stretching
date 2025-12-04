# База данных Cohai Stretching — целевая схема v1 (draft)

Цель v1-схемы — привести БД в согласие с реальным бизнесом
(мобильное приложение + Instagram) и потребностями сайта:

- локации и их зоны (зал / парк),
- направления тренировок,
- расписание,
- абонементы / цены,
- тренеры,
- лиды,
- маркетинговый контент (кейсы, отзывы, лояльность, вакансии).

Важно: v1 должна быть **эволюцией** v0 (миграции без сноса данных).

---

## 1. Каталог: локации, зоны, направления, тренеры

### 1.1. Таблица `locations` (расширение текущей)

**v0:**

- `id` INTEGER PK
- `name` VARCHAR(200) NOT NULL
- `address` VARCHAR(300) NULL

**v1 (план):**

- `id` INTEGER PK
- `name` VARCHAR(200) NOT NULL          — название студии/филиала
- `address` VARCHAR(300) NULL           — человекочитаемый адрес
- `city` VARCHAR(100) NULL              — город (Chişinău и т.п.)
- `latitude` REAL NULL                  — широта на карте
- `longitude` REAL NULL                 — долгота
- `is_active` BOOLEAN NOT NULL DEFAULT 1 — активна ли локация (на будущее)

---

### 1.2. Таблица `location_areas` (НОВАЯ)

Зоны внутри локации: основной зал, парк, отдельные комнаты и т.п.

- `id` INTEGER PK
- `location_id` INTEGER NOT NULL        — FK → locations.id
- `name` VARCHAR(100) NOT NULL          — напр. "Главный зал", "Парк Valea Morilor"
- `is_outdoor` BOOLEAN NOT NULL DEFAULT 0
- `is_active` BOOLEAN NOT NULL DEFAULT 1

---

### 1.3. Таблица `program_types` (расширение текущей)

**v0:**

- `id` INTEGER PK
- `name` VARCHAR(100) NOT NULL
- `description` VARCHAR(255) NULL
- `is_group` BOOLEAN NOT NULL

**v1 (план):**

- `id` INTEGER PK
- `slug` VARCHAR(100) NOT NULL UNIQUE   — "active_stretch", "classic_stretch", "kids_gym"
- `name` VARCHAR(100) NOT NULL          — человекочитаемое название (RU)
- `name_ro` VARCHAR(100) NULL           — название (RO)
- `description` VARCHAR(500) NULL
- `category` VARCHAR(50) NOT NULL       — ENUM-подобное: "GROUP", "PERSONAL", "PARK", "KIDS", "MEN", "FEMALE"
- `is_group` BOOLEAN NOT NULL           — как в v0, оставляем для совместимости
- `target_audience` VARCHAR(100) NULL   — "взрослые", "дети", "мужчины", "беременные", ...
- `is_active` BOOLEAN NOT NULL DEFAULT 1

---

### 1.4. Таблица `trainers` (легкое расширение)

**v0:**

- `id` INTEGER PK
- `full_name` VARCHAR(100) NOT NULL
- `phone` VARCHAR(50) NULL
- `email` VARCHAR(100) NULL

**v1 (план):**

- `id` INTEGER PK
- `full_name` VARCHAR(100) NOT NULL
- `phone` VARCHAR(50) NULL
- `email` VARCHAR(100) NULL
- `bio` TEXT NULL                       — краткое описание тренера
- `photo_url` VARCHAR(255) NULL         — ссылка на фото
- `is_active` BOOLEAN NOT NULL DEFAULT 1
- `sort_order` INTEGER NOT NULL DEFAULT 0 — порядок отображения на сайте

---

## 2. Абонементы / цены

Сейчас есть таблица `membership_plans` — мы её расширим,
чтобы покрыть прайс-листы (групповые, персональные, дуо/трио, парк).

### 2.1. Таблица `membership_plans` (расширение текущей)

**v0:**

- `id` INTEGER PK
- `name` VARCHAR(100) NOT NULL
- `description` VARCHAR(255) NULL
- `price` INTEGER NOT NULL
- `location_id` INTEGER NOT NULL

**v1 (план):**

- `id` INTEGER PK
- `name` VARCHAR(100) NOT NULL          — "4 занятия", "10 тренировок персонально", ...
- `description` VARCHAR(500) NULL
- `location_id` INTEGER NOT NULL        — FK → locations.id (где действует)
- `program_type_id` INTEGER NULL        — FK → program_types.id (если привязан к формату)
- `plan_type` VARCHAR(50) NOT NULL      — "GROUP", "PARK", "PERSONAL_INDIVIDUAL", "PERSONAL_DUO", "PERSONAL_TRIO"
- `sessions_count` INTEGER NULL         — кол-во занятий (4, 8, 10, 12...). NULL для разовых/пробных.
- `price` INTEGER NOT NULL              — базовая цена (леев)
- `valid_days` INTEGER NULL             — срок действия абонемента в днях (30/40 и т.п.)
- `is_trial` BOOLEAN NOT NULL DEFAULT 0 — пробное занятие
- `is_single` BOOLEAN NOT NULL DEFAULT 0 — разовая тренировка
- `is_special_renewal` BOOLEAN NOT NULL DEFAULT 0
- `special_price` INTEGER NULL          — цена при продлении (из прайса)
- `is_active` BOOLEAN NOT NULL DEFAULT 1

---

## 3. Расписание

В v0 таблица `class_sessions` уже играет роль «слотов расписания».
В v1 мы формализуем это как **шаблон недельного расписания**.

### 3.1. Таблица `class_sessions` (интерпретация как недельные слоты)

**v0:**

- `id` INTEGER PK
- `location_id` INTEGER NOT NULL
- `program_type_id` INTEGER NOT NULL
- `trainer_id` INTEGER NOT NULL
- `membership_plan_id` INTEGER NULL
- `weekday` INTEGER NOT NULL
- `start_time` TIME NOT NULL
- `end_time` TIME NOT NULL
- `capacity` INTEGER NOT NULL
- `is_active` BOOLEAN NOT NULL

**v1 (план, как weekly-slot):**

- `id` INTEGER PK
- `location_area_id` INTEGER NOT NULL       — FK → location_areas.id
- `program_type_id` INTEGER NOT NULL        — FK → program_types.id
- `trainer_id` INTEGER NOT NULL             — FK → trainers.id
- `membership_plan_id` INTEGER NULL         — FK → membership_plans.id (если есть «рекомендованный» план)
- `weekday` INTEGER NOT NULL                — 1–7 (или 0–6, зафиксируем)
- `start_time` TIME NOT NULL
- `end_time` TIME NOT NULL
- `capacity` INTEGER NOT NULL
- `level` VARCHAR(50) NULL                  — "beginner", "intermediate" (на будущее)
- `is_active` BOOLEAN NOT NULL
- (опционально) `is_for_kids` BOOLEAN       — только для детей
- (опционально) `is_for_men` BOOLEAN
- (опционально) `is_female_styles` BOOLEAN

> Примечание: **пока не вводим отдельную таблицу для "разовых" ClassInstance по датам**.
> Это можно будет добавить позже, когда появится запись на конкретные даты.

---

## 4. Лиды

### 4.1. Таблица `leads` (легкое расширение)

**v0:**

- `id` INTEGER PK
- `full_name` VARCHAR NOT NULL
- `phone` VARCHAR NOT NULL
- `source` VARCHAR NULL
- `location_id` INTEGER NULL
- `program_type_id` INTEGER NULL
- `is_processed` BOOLEAN NOT NULL
- `created_at` DATETIME NOT NULL

**v1 (план):**

- `id` INTEGER PK
- `full_name` VARCHAR NOT NULL
- `phone` VARCHAR NOT NULL
- `email` VARCHAR NULL
- `source` VARCHAR NULL                  — "site", "instagram", "friend"
- `location_id` INTEGER NULL             — FK → locations.id
- `program_type_id` INTEGER NULL         — FK → program_types.id
- `comment` VARCHAR(500) NULL            — свободный текст
- `is_processed` BOOLEAN NOT NULL
- `created_at` DATETIME NOT NULL

---

## 5. Маркетинг-контент

Этого в v0 нет; в v1 добавляем новые таблицы.

### 5.1. Таблица `reviews` (НОВАЯ)

Отзывы клиентов (для сайта и, возможно, для приложения).

- `id` INTEGER PK
- `author_name` VARCHAR(100) NULL        — можно оставить пустым
- `text` TEXT NOT NULL
- `created_at` DATETIME NOT NULL
- `is_published` BOOLEAN NOT NULL DEFAULT 0

---

### 5.2. Таблица `cases` (НОВАЯ)

Кейсы / истории (например, «беременность 38 недель»).

- `id` INTEGER PK
- `slug` VARCHAR(100) NOT NULL UNIQUE    — для URL
- `title` VARCHAR(200) NOT NULL
- `summary` VARCHAR(500) NULL
- `description` TEXT NOT NULL
- `image_url` VARCHAR(255) NULL
- `category` VARCHAR(100) NULL           — "pregnancy", "back_pain", ...
- `created_at` DATETIME NOT NULL
- `is_published` BOOLEAN NOT NULL DEFAULT 0

#### 5.2.1. Таблица `case_program_types` (связь Many-to-Many, НОВАЯ)

- `case_id` INTEGER NOT NULL             — FK → cases.id
- `program_type_id` INTEGER NOT NULL     — FK → program_types.id
- PRIMARY KEY (`case_id`, `program_type_id`)

---

### 5.3. Таблицы `loyalty_programs` и `loyalty_bonuses` (НОВЫЕ)

Программа лояльности (из сторис про «приведи друга — получи тренировки»).

#### `loyalty_programs`

- `id` INTEGER PK
- `title` VARCHAR(200) NOT NULL
- `description` TEXT NULL
- `date_start` DATE NOT NULL
- `date_end` DATE NOT NULL
- `is_active` BOOLEAN NOT NULL DEFAULT 0

#### `loyalty_bonuses`

- `id` INTEGER PK
- `program_id` INTEGER NOT NULL          — FK → loyalty_programs.id
- `friends_count` INTEGER NOT NULL       — 1, 2, 3, ...
- `bonus_sessions` INTEGER NOT NULL      — сколько занятий даётся

---

### 5.4. Таблицы `job_openings` и `job_applications` (НОВЫЕ)

Вакансии тренеров и отклики.

#### `job_openings`

- `id` INTEGER PK
- `title` VARCHAR(200) NOT NULL          — "Тренер по растяжке"
- `description` TEXT NOT NULL            — что за должность
- `requirements` TEXT NOT NULL           — требования (как в сторис)
- `is_active` BOOLEAN NOT NULL DEFAULT 1
- `created_at` DATETIME NOT NULL

#### `job_applications`

- `id` INTEGER PK
- `job_opening_id` INTEGER NOT NULL      — FK → job_openings.id
- `full_name` VARCHAR(100) NOT NULL
- `phone` VARCHAR(50) NOT NULL
- `email` VARCHAR(100) NULL
- `experience_text` TEXT NULL            — "о себе / опыт"
- `cv_url` VARCHAR(255) NULL             — ссылка на резюме (гугл-диск и т.п.)
- `status` VARCHAR(20) NOT NULL DEFAULT "NEW"  — "NEW", "VIEWED", "REJECTED", "APPROVED"
- `created_at` DATETIME NOT NULL

---

## 6. Итог по v1 (сдвиги относительно v0)

**Модифицируемые таблицы:**

- `locations` → добавляем город, координаты, is_active.
- `program_types` → slug, category, name_ro, target_audience, is_active.
- `trainers` → bio, photo_url, is_active, sort_order.
- `membership_plans` → превращаем в полноценные "прайс-планы".
- `class_sessions` → чётко трактуем как недельные слоты; заменяем location_id → location_area_id, добавляем опциональные флаги.
- `leads` → добавляем email, comment.

**Новые таблицы:**

- `location_areas`
- `reviews`
- `cases`
- `case_program_types`
- `loyalty_programs`
- `loyalty_bonuses`
- `job_openings`
- `job_applications`

---

## 7. План действий после утверждения схемы v1

1. Обновить SQLAlchemy-модели под эту схему.
2. Подготовить Alembic-миграцию:
   - новые таблицы,
   - ALTER TABLE для существующих.
3. Аккуратно адаптировать `bootstrap_db.py` под v1:
   - реальные направления из инсты,
   - реальные абонементы из прайс-листа,
   - реальные расписания (по сторис),
   - заглушки кейсов/отзывов/лояльности/вакансий.
4. Обновить публичные эндпоинты `/public/...` для работы с новой схемой.
