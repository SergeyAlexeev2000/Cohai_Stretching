"""
Utility script to debug imports in the Cohai Stretching backend.

Run from the project root, for example:

    ./.venv/Scripts/python app/tools/debug_imports.py

or just:

    python app/tools/debug_imports.py

(если venv активирован)

Скрипт:
- добавляет корень проекта в sys.path
- проверяет импорты моделей, репозиториев, схем, сервисов, api и main
"""

from __future__ import annotations

import importlib
import sys
import traceback
from pathlib import Path


# ===== A. Fix sys.path so that `import app` always works =====

THIS_FILE = Path(__file__).resolve()
# app/tools/debug_imports.py -> parents[2] == корень проекта
PROJECT_ROOT = THIS_FILE.parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ===== B. Helper to check blocks of imports =====

def check_block(title: str, modules: list[str]) -> bool:
    """
    Try to import each module in `modules`.

    Returns:
        True  if all modules imported successfully,
        False if at least one failed.
    """
    print(f"\n===== {title} =====")
    all_ok = True

    for mod_name in modules:
        print(f"\n--- importing {mod_name} ---")

        try:
            m = importlib.import_module(mod_name)
        except Exception:
            all_ok = False
            print(f"FAILED: {mod_name}")
            traceback.print_exc()
        else:
            public = [n for n in dir(m) if not n.startswith("_")]
            print(f"OK: {mod_name}")
            print(f"public names: {public}")

    return all_ok


# ===== C. Main routine =====

def main() -> None:
    everything_ok = True

    # 1. MODELS
    models_ok = check_block(
        "A. MODELS",
        [
            "app.models.location",
            "app.models.membership",
            "app.models.program_type",
            "app.models.trainer",
            "app.models.class_session",
        ],
    )
    everything_ok &= models_ok

    # 2. REPOSITORIES
    repos_ok = check_block(
        "B. REPOSITORIES",
        [
            "app.repositories.location_repo",
            "app.repositories.membership_repo",
            "app.repositories.program_type_repo",
            "app.repositories.lead_repo",
            "app.repositories.class_session_repo",
        ],
    )
    everything_ok &= repos_ok

    # 3. SCHEMAS
    schemas_ok = check_block(
        "C. SCHEMAS",
        [
            "app.schemas.location",
            "app.schemas.membership",
            "app.schemas.program_type",
            "app.schemas.lead",
            "app.schemas.class_session",
        ],
    )
    everything_ok &= schemas_ok

    # 4. SERVICES
    services_ok = check_block(
        "D. SERVICES",
        [
            "app.services.lead_service",
            "app.services.membership_service",
            "app.services.schedule_service",
        ],
    )
    everything_ok &= services_ok

    # 5. API
    api_ok = check_block(
        "E. API",
        [
            "app.api.v1.public",
            "app.api.v1.admin_leads",
        ],
    )
    everything_ok &= api_ok

    # 6. MAIN
    main_ok = check_block(
        "F. MAIN",
        [
            "app.main",
        ],
    )
    everything_ok &= main_ok

    print("\n===== SUMMARY =====")
    if everything_ok:
        print("All imports OK ✅")
    else:
        print("Some imports FAILED ❌  (см. выше трассировки)")


if __name__ == "__main__":
    main()