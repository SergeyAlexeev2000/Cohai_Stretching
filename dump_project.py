import os

# Корневая папка проекта (можно оставить "." если запускаешь из корня)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Куда писать результат
OUTPUT_FILE = os.path.join(ROOT_DIR, "project_dump.txt")

# Какие расширения собирать (можешь добавить .js, .ts, .html, .css и т.д.)
INCLUDE_EXT = {".py", ".md", ".db", ".json", ".html", ".css", ".js", ".ts", ".txt"}
  

# Какие папки пропускать
EXCLUDE_DIRS = {
    ".git", ".idea", ".vscode",
    "__pycache__", ".venv", "venv", "env",
    "node_modules", "dist", "build",
}

def should_skip_dir(dirname: str) -> bool:
    return dirname in EXCLUDE_DIRS

def should_include_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename)
    return ext in INCLUDE_EXT

def main():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for root, dirs, files in os.walk(ROOT_DIR):
            # фильтруем папки на лету
            dirs[:] = [d for d in dirs if not should_skip_dir(d)]

            for fname in files:
                if not should_include_file(fname):
                    continue

                full_path = os.path.join(root, fname)
                rel_path = os.path.relpath(full_path, ROOT_DIR)

                out.write("\n" + "=" * 80 + "\n")
                out.write(f"# FILE: {rel_path}\n")
                out.write("=" * 80 + "\n\n")

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        out.write(f.read())
                except UnicodeDecodeError:
                    out.write("[[Не удалось прочитать файл в utf-8]]\n")

    print(f"Готово! Все файлы собраны в: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()