# База данных Cohai Stretching — схема v0 (legacy)

Этот документ описывает **фактическую** структуру таблиц в `cohai_stretching.db`
на момент 2025-11-24 (до рефакторинга backend-а).

Снимок структуры получен через:

```bash
sqlite3 cohai_stretching.db ".tables"
sqlite3 cohai_stretching.db "PRAGMA table_info(<table_name>);"

locations
---------
id          INTEGER        PRIMARY KEY AUTOINCREMENT
name        VARCHAR(200)   NOT NULL
address     VARCHAR(300)   NULL

program_types
-------------
id          INTEGER        PRIMARY KEY AUTOINCREMENT
name        VARCHAR(100)   NOT NULL
description VARCHAR(255)   NULL
is_group    BOOLEAN        NOT NULL

trainers
--------
id          INTEGER        PRIMARY KEY AUTOINCREMENT
full_name   VARCHAR(100)   NOT NULL
phone       VARCHAR(50)    NULL
email       VARCHAR(100)   NULL

membership_plans
----------------
id          INTEGER        PRIMARY KEY AUTOINCREMENT
name        VARCHAR(100)   NOT NULL
description VARCHAR(255)   NULL
price       INTEGER        NOT NULL
location_id INTEGER        NOT NULL   -- FK → locations.id (логическая)

class_sessions
--------------
id                  INTEGER      PRIMARY KEY AUTOINCREMENT
location_id         INTEGER      NOT NULL   -- FK → locations.id (логическая)
program_type_id     INTEGER      NOT NULL   -- FK → program_types.id
trainer_id          INTEGER      NOT NULL   -- FK → trainers.id
membership_plan_id  INTEGER      NULL       -- FK → membership_plans.id (опционально)
weekday             INTEGER      NOT NULL
start_time          TIME         NOT NULL
end_time            TIME         NOT NULL
capacity            INTEGER      NOT NULL
is_active           BOOLEAN      NOT NULL

leads
-----
id             INTEGER      PRIMARY KEY AUTOINCREMENT
full_name      VARCHAR      NOT NULL
phone          VARCHAR      NOT NULL
source         VARCHAR      NULL
location_id    INTEGER      NULL    -- FK → locations.id (логическая)
program_type_id INTEGER     NULL    -- FK → program_types.id
is_processed   BOOLEAN      NOT NULL
created_at     DATETIME     NOT NULL
