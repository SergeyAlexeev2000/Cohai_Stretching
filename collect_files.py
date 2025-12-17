import sys
import glob
from pathlib import Path

def collect_files(patterns, output="backend_snapshot.txt"):
    """
    Собирает содержимое всех файлов, совпадающих с переданными паттернами,
    и пишет в единый txt-файл.
    """
    output_path = Path(output)
    collected = []

    for pattern in patterns:
        # glob рекурсивно ищет файлы по шаблону
        files = sorted(Path(".").glob(pattern))
        if not files:
            print(f"[WARN] pattern '{pattern}' did not match any files")
            continue

        for filepath in files:
            if filepath.is_file():
                print(f"[ADD] {filepath}")
                text = filepath.read_text(encoding="utf-8", errors="ignore")
                collected.append(
                    f"\n\n# ===== FILE: {filepath} =====\n\n{text}\n"
                )

    output_path.write_text("".join(collected), encoding="utf-8")
    print(f"\n[OK] Snapshot saved to: {output_path.absolute()}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:\n  python collect_files.py <pattern1> <pattern2> ... [output=...]")
        sys.exit(1)

    args = sys.argv[1:]

    # Если последний аргумент выглядит как output=file.txt
    output = "backend_snapshot.txt"
    if args[-1].startswith("output="):
        output = args[-1].split("=", 1)[1]
        patterns = args[:-1]
    else:
        patterns = args

    collect_files(patterns, output)
