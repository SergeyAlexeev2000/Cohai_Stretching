# Cohai Stretching – Project Architecture

Корень проекта (локально): `D:/Cohai_Stretching`

```text
D:/Cohai_Stretching
├─ app/
│  ├─ __init__.py
│  ├─ main.py                # точка входа FastAPI
│  │
│  ├─ core/
│  │  ├─ __init__.py
│  │  ├─ config.py           # настройки (env, пути, debug)
│  │  ├─ logging.py          # настройка логгера
│  │  └─ exceptions.py       # AppError, глобальный handler
│  │
│  ├─ db/
│  │  ├─ __init__.py
│  │  ├─ base.py             # Base = declarative_base()
│  │  └─ session.py          # engine, SessionLocal
│  │
│  ├─ models/
│  │  ├─ __init__.py
│  │  ├─ location.py         # Location
│  │  ├─ program_type.py     # ProgramType
│  │  ├─ trainer.py          # Trainer
│  │  ├─ membership.py       # MembershipPlan
│  │  └─ class_session.py    # ClassSession
│  │
│  ├─ repositories/
│  │  ├─ __init__.py
│  │  ├─ location_repo.py
│  │  ├─ program_type_repo.py
│  │  ├─ membership_repo.py
│  │  ├─ trainer_repo.py
│  │  ├─ class_session_repo.py
│  │  └─ lead_repo.py
│  │
│  ├─ schemas/
│  │  ├─ __init__.py
│  │  ├─ location.py
│  │  ├─ program_type.py
│  │  ├─ membership.py
│  │  ├─ class_session.py
│  │  └─ lead.py
│  │
│  ├─ services/
│  │  ├─ __init__.py
│  │  ├─ schedule_service.py
│  │  ├─ membership_service.py
│  │  └─ lead_service.py
│  │
│  ├─ api/
│  │  ├─ __init__.py
│  │  └─ v1/
│  │     ├─ __init__.py
│  │     ├─ public.py        # публичные эндпоинты
│  │     └─ admin_leads.py   # админские эндпоинты для лидов
│  │
│  ├─ tools/
│  │  ├─ __init__.py
│  │  ├─ debug_imports.py    # проверка импортов
│  │  ├─ check_sqlalchemy.py # проверка мапперов
│  │  └─ bootstrap_db.py     # создание таблиц + тестовые данные
│  │
│  ├─ logs/
│  │  └─ app.log
│  │
│  └─ plan_tracker.py        # CLI-утилита с глобальным планом
│
├─ cohai_stretching.db       # SQLite база
├─ requirements.txt
└─ (прочие файлы проекта)
