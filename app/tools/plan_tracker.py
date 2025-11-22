"""
Небольшой трекер прогресса по backend-плану.

Использование:

  # показать все шаги
  python app/tools/plan_tracker.py list

  # пометить шаг 1 как ЗАКРЫТ
  python app/tools/plan_tracker.py done 1

  # пометить шаг 2 как "мы сейчас здесь"
  python app/tools/plan_tracker.py current 2
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
PLAN_PATH = ROOT_DIR / "cohai_backend_plan.md"

# Разрешаем заголовки как:
# "Шаг 1 — ..."
# "# Шаг 1 — ..."
# "## Шаг 1 — ..."
STEP_RE = re.compile(
    r"^(?P<prefix>#+\s*)?(?P<body>Шаг\s+(?P<num>\d+)\b.*)$",
    re.MULTILINE,
)


def load_plan() -> str:
    return PLAN_PATH.read_text(encoding="utf-8")


def save_plan(text: str) -> None:
    PLAN_PATH.write_text(text, encoding="utf-8")


def list_steps() -> None:
    text = load_plan()
    matches = list(STEP_RE.finditer(text))
    if not matches:
        print("Шаги в файле не найдены.")
        return
    print(f"Найдено шагов: {len(matches)}\n")
    for m in matches:
        # Показываем только "Шаг N — ..." без решёток
        line = m.group("body").strip()
        print(line)


def mark_done(step: int) -> None:
    text = load_plan()

    def repl(m: re.Match) -> str:
        prefix = m.group("prefix") or ""
        line = m.group("body")
        num = int(m.group("num"))

        # убираем старые пометки
        line = line.replace("(мы сейчас здесь)", "")
        line = re.sub(r"—\s*✅.*", "", line)
        line = re.sub(r"\s+", " ", line).strip()

        if num == step:
            return f"{prefix}{line} — ✅ ЗАКРЫТ"
        else:
            return f"{prefix}{line}"

    new_text, count = STEP_RE.subn(repl, text)
    if count == 0:
        print(f"Не найден Шаг {step} в {PLAN_PATH.name}")
        return

    save_plan(new_text)
    print(f"Шаг {step} помечен как ЗАКРЫТ.")


def mark_current(step: int) -> None:
    text = load_plan()

    def repl(m: re.Match) -> str:
        prefix = m.group("prefix") or ""
        line = m.group("body")
        num = int(m.group("num"))

        # чистим старые пометки
        line = line.replace("(мы сейчас здесь)", "")
        line = re.sub(r"—\s*✅.*", "", line)
        line = re.sub(r"\s+", " ", line).strip()

        if num == step:
            return f"{prefix}{line} (мы сейчас здесь)"
        else:
            return f"{prefix}{line}"

    new_text, count = STEP_RE.subn(repl, text)
    if count == 0:
        print(f"Не найден Шаг {step} в {PLAN_PATH.name}")
        return

    save_plan(new_text)
    print(f"Шаг {step} помечен как 'мы сейчас здесь'.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Трекер прогресса backend-плана.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="Показать все шаги в плане.")

    p_done = sub.add_parser("done", help="Пометить шаг как ЗАКРЫТ.")
    p_done.add_argument("step", type=int, help="Номер шага (например, 1).")

    p_cur = sub.add_parser("current", help="Пометить шаг как 'мы сейчас здесь'.")
    p_cur.add_argument("step", type=int, help="Номер шага (например, 2).")

    args = parser.parse_args()

    if args.cmd == "list":
        list_steps()
    elif args.cmd == "done":
        mark_done(args.step)
    elif args.cmd == "current":
        mark_current(args.step)
    else:
        parser.error("Неизвестная команда")


if __name__ == "__main__":
    main()
