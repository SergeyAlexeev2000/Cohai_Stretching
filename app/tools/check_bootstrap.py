"""
Diagnostic tool for app.tools.bootstrap_db.

Запускать из корня проекта:

    python -m app.tools.check_bootstrap

Что делает:

A. Проверяет, что модуль app.tools.bootstrap_db импортируется.
B. Находит и проверяет функцию bootstrap().
C. Показывает, какие ORM-модели импортированы в модуль.
D. Запускает bootstrap() с подробным логом и трассировкой ошибки.
E. Проверяет содержимое БД по ключевым таблицам.
"""

from __future__ import annotations

import importlib
import inspect
import traceback
from pathlib import Path
from typing import Any, List, Tuple, Type

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.session import engine
from app.db.base import Base

from app.models.location import Location
from app.models.program_type import ProgramType
from app.models.membership import MembershipPlan
from app.models.trainer import Trainer
from app.models.class_session import ClassSession
from app.models.lead import Lead


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def section(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def line(msg: str) -> None:
    print(msg, flush=True)


def inspect_models_in_module(mod) -> List[Type[Any]]:
    """Ищем классы с __tablename__ в модуле bootstrap_db."""
    models: List[Type[Any]] = []
    for name, obj in vars(mod).items():
        if inspect.isclass(obj) and hasattr(obj, "__tablename__"):
            models.append(obj)
    return models


def count_rows(session: Session, model: Type[Any]) -> Tuple[int, bool]:
    """
    Возвращает (count, ok), где ok=False если таблицы нет или маппинг не работает.
    """
    try:
        stmt = select(func.count()).select_from(model)
        count = session.scalar(stmt) or 0
        return int(count), True
    except Exception:
        traceback.print_exc()
        return 0, False


# -------------------------------------------------------------------
# Main diagnostic
# -------------------------------------------------------------------

def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    section("0. Environment")
    line(f"Project root: {project_root}")
    line(f"Engine URL:  {engine.url}")

    # --- A. Import bootstrap module ---
    section("A. Import app.tools.bootstrap_db")

    try:
        boot_mod = importlib.import_module("app.tools.bootstrap_db")
        line(f"[OK] Imported app.tools.bootstrap_db from: {Path(boot_mod.__file__).resolve()}")
    except Exception:
        line("[FAIL] Cannot import app.tools.bootstrap_db:")
        traceback.print_exc()
        return

    # --- B. Inspect bootstrap() function ---
    section("B. Inspect bootstrap() function")

    bootstrap = getattr(boot_mod, "bootstrap", None)
    if bootstrap is None or not callable(bootstrap):
        line("[FAIL] bootstrap() not found or not callable in app.tools.bootstrap_db")
        return

    sig = inspect.signature(bootstrap)
    line(f"[OK] Found bootstrap() with signature: {sig}")
    if sig.parameters:
        line("[WARN] bootstrap() has parameters — ожидалось без аргументов")

    # --- C. What models are visible inside bootstrap_db ---
    section("C. ORM models visible in app.tools.bootstrap_db")

    models_in_mod = inspect_models_in_module(boot_mod)
    if not models_in_mod:
        line("[WARN] No ORM models with __tablename__ found in module namespace.")
    else:
        line(f"[OK] Found {len(models_in_mod)} model classes in bootstrap_db:")
        for m in models_in_mod:
            line(f"  • {m.__name__}  (table: {m.__tablename__})")

    # --- D. Run bootstrap() with detailed error reporting ---
    section("D. Running bootstrap()")

    try:
        bootstrap()
        line("[OK] bootstrap() finished without raising an exception.")
    except Exception:
        line("[FAIL] bootstrap() raised an exception:")
        traceback.print_exc()
        # имеет смысл всё равно посмотреть, что в БД после частичного выполнения
        # поэтому НЕ делаем return здесь

    # --- E. Inspect DB contents ---
    section("E. Inspecting DB contents after bootstrap()")

    with Session(engine) as session:
        checks: List[Tuple[str, Type[Any]]] = [
            ("Location", Location),
            ("ProgramType", ProgramType),
            ("MembershipPlan", MembershipPlan),
            ("Trainer", Trainer),
            ("ClassSession", ClassSession),
            ("Lead", Lead),
        ]

        for label, model in checks:
            line(f"\n→ Checking table for {label} (model: {model.__name__})")
            if not hasattr(model, "__tablename__"):
                line("  [FAIL] Model has no __tablename__ attribute.")
                continue

            line(f"  table name: {model.__tablename__}")

            count, ok = count_rows(session, model)
            if ok:
                line(f"  [OK] Row count: {count}")
            else:
                line("  [FAIL] Could not query this model (см. стек выше).")

    section("F. Done")
    line("check_bootstrap.py finished.\n")


if __name__ == "__main__":
    main()
