# app/tools/check_sqlalchemy.py
from __future__ import annotations

"""
Super-verbose SQLAlchemy checker for Cohai Stretching.

Запускать из корня проекта, например:

    ./.venv/Scripts/python app/tools/check_sqlalchemy.py

или, если venv активирован:

    python app/tools/check_sqlalchemy.py
"""

import sys
import traceback
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import configure_mappers

# ===== A. Fix sys.path so that `import app` always works =====

THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parents[2]  # .../Cohai_Stretching

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ===== B. Helper: pretty printing =====

def header(title: str) -> None:
    print(f"\n===== {title} =====")


def sub(title: str) -> None:
    print(f"\n--- {title} ---")


# ===== C. Helper: import block (как в debug_imports.py) =====

def import_block(title: str, modules: list[str]) -> bool:
    """
    Импортирует каждый модуль из списка и печатает:
    - OK + список публичных имён
    - либо FAILED + traceback.
    """
    header(title)
    all_ok = True

    for mod_name in modules:
        print(f"\n... importing {mod_name}")
        try:
            m = __import__(mod_name, fromlist=["*"])
        except Exception:
            all_ok = False
            print(f"❌ FAILED: {mod_name}")
            traceback.print_exc()
        else:
            public = [n for n in dir(m) if not n.startswith("_")]
            print(f"✅ OK: {mod_name}")
            print(f"   public names: {public}")

    return all_ok


# ===== D. Main routine =====

def main() -> None:
    header("SQLAlchemy configuration check")
    print(f"Project root: {PROJECT_ROOT}")

    everything_ok = True

    # 1. Импорт моделей
    models_ok = import_block(
        "A. MODELS IMPORT",
        [
            "app.models.location",
            "app.models.membership",
            "app.models.program_type",
            "app.models.trainer",
            "app.models.class_session",
            "app.models.lead",
        ],
    )
    if not models_ok:
        print("\n⚠️  Some model modules failed to import – дальше проверка ORM может быть бессмысленна.")
    everything_ok &= models_ok

    # Теперь, когда модели импортированы, можно тянуть Base и SessionLocal
    from app.db.base import Base
    from app.db.session import SessionLocal

    # 2. Зарегистрированные мапперы
    header("B. REGISTERED MAPPERS (Base.registry.mappers)")
    mappers = list(Base.registry.mappers)
    if not mappers:
        print("⚠️  No mappers found in Base.registry.mappers")
        everything_ok = False
    else:
        print(f"Found {len(mappers)} mappers:\n")
        for mapper in mappers:
            cls = mapper.class_
            table = mapper.local_table
            print(f"• {cls.__name__}  -> table '{table.name}'")
            # колонки
            cols = [c.name for c in table.columns]
            print(f"   columns: {cols}")
            # связи
            if mapper.relationships:
                rels = [
                    f"{rel.key} -> {rel.mapper.class_.__name__}"
                    for rel in mapper.relationships
                ]
                print(f"   relationships: {rels}")
            else:
                print("   relationships: []")

    # 3. configure_mappers()
    header("C. CONFIGURE_MAPPERS()")
    try:
        configure_mappers()
    except Exception as exc:
        everything_ok = False
        print("❌ Mapper configuration FAILED!")
        print("Exception:", repr(exc))
        print("\nTraceback:")
        traceback.print_exc()
        # если конфигурация не прошла — дальше нет смысла идти
        header("SUMMARY")
        print("SQLAlchemy status: FAILED ❌ (см. выше traceback в C. CONFIGURE_MAPPERS)")
        return
    else:
        print("✅ Mappers configured successfully.")

    # 4. Простые SELECT'ы
    header("D. SIMPLE SELECT FROM EACH MODEL")
    with SessionLocal() as db:
        for mapper in mappers:
            cls = mapper.class_
            try:
                db.execute(select(cls).limit(1)).first()
            except Exception as exc:
                everything_ok = False
                print(f"❌ [FAIL] {cls.__name__}: {exc!r}")
                traceback.print_exc()
            else:
                print(f"✅ [OK]   {cls.__name__}: select(1) succeeded")

    # 5. Итог
    header("SUMMARY")
    if everything_ok:
        print("SQLAlchemy status: OK ✅ (imports + mappers + simple selects)")
    else:
        print("SQLAlchemy status: Some checks FAILED ❌ (см. подробности выше)")


if __name__ == "__main__":
    main()