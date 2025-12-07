from __future__ import annotations

from pathlib import Path

# Какие директории не хотим видеть в дереве
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
    "node_modules",
    "dist",
    "build",
}

# Какие файлы можно пропустить (по расширению) – при желании добавь
EXCLUDED_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".log",
    ".db-journal",
}


def is_hidden(path: Path) -> bool:
    """Скрытые файлы/папки (начинаются с точки), кроме явно разрешённых."""
    name = path.name
    if name in {".vscode"}:
        return False
    return name.startswith(".")


def iter_children(path: Path) -> list[Path]:
    """Дети каталога, отсортированные: сначала папки, потом файлы."""
    children = [p for p in path.iterdir()]

    def sort_key(p: Path):
        return (p.is_file(), p.name.lower())

    return sorted(children, key=sort_key)


def build_tree(root: Path, prefix: str = "") -> list[str]:
    """Рекурсивно строим дерево файлов и папок, возвращаем список строк."""
    lines: list[str] = []
    children = [p for p in iter_children(root) if not is_hidden(p)]

    # фильтруем исключённые директории и файлы
    filtered: list[Path] = []
    for child in children:
        if child.is_dir() and child.name in EXCLUDED_DIRS:
            continue
        if child.is_file() and child.suffix in EXCLUDED_EXTENSIONS:
            continue
        filtered.append(child)

    last_index = len(filtered) - 1

    for idx, child in enumerate(filtered):
        connector = "└── " if idx == last_index else "├── "
        lines.append(f"{prefix}{connector}{child.name}")

        if child.is_dir():
            extension = "    " if idx == last_index else "│   "
            lines.extend(build_tree(child, prefix + extension))

    return lines


def main() -> None:
    project_root = Path(__file__).resolve().parent  # корень = где лежит данный скрипт
    output_path = project_root / "project_tree.md"  # можешь поменять на .txt

    header = f"# Project tree: {project_root.name}\n\n"
    header += "```text\n"
    tree_lines = [project_root.name]
    tree_lines.extend(build_tree(project_root))

    text = header + "\n".join(tree_lines) + "\n```" + "\n"

    output_path.write_text(text, encoding="utf-8")
    print(f"Tree saved to: {output_path}")


if __name__ == "__main__":
    main()
