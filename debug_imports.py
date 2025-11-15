# debug_imports.py
"""
Пошаговая проверка импорта слоёв:

A. Модели
B. Репозитории
C. API
D. main-приложение
"""

import importlib
import traceback


def check_block(title: str, modules: list[str]) -> bool:
    print(f"\n===== {title} =====")
    for name in modules:
        print(f"\n--- importing {name} ---")
        try:
            m = importlib.import_module(name)
            print("OK:", name)
            # Покажем, какие "нормальные" имена экспортируются
            public_names = [n for n in dir(m) if not n.startswith("_")]
            print("public names:", public_names)
        except Exception:
            print("FAILED:", name)
            traceback.print_exc()
            return False
    return True


def main():
    # A. MODELS
    models = [
        "app.models.location",
        "app.models.membership",
        "app.models.program_type",
        "app.models.trainer",
        "app.models.class_session",
    ]
    if not check_block("A. MODELS", models):
        return

    # B. REPOSITORIES
    repos = [
        "app.repositories.location_repo",
        "app.repositories.membership_repo",
        "app.repositories.program_type_repo",
        "app.repositories.lead_repo",
        "app.repositories.class_session_repo",
    ]
    if not check_block("B. REPOSITORIES", repos):
        return

    # C. API
    api_modules = [
        "app.api.v1.deps",
        "app.api.v1.public",
        "app.api.v1.admin_leads",
    ]
    if not check_block("C. API", api_modules):
        return

    # D. MAIN
    print("\n===== D. MAIN =====")
    try:
        m = importlib.import_module("app.main")
        print("OK: app.main imported from", m.__file__)
        print("Has attribute 'app':", hasattr(m, "app"))
    except Exception:
        print("FAILED: app.main")
        traceback.print_exc()
        return

    print("\nAll imports OK ✅")


if __name__ == "__main__":
    main()
