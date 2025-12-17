import sys
from pathlib import Path

def search(root: str, pattern: str, mask: str = "**/*.py") -> None:
    root_path = Path(root)
    if not root_path.exists():
        print(f"[ERR] root '{root}' does not exist")
        return

    print(f"[INFO] Searching for '{pattern}' in {root}/{mask}\n")

    for path in root_path.rglob(mask.split("/", 1)[-1]):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"[WARN] cannot read {path}: {e}")
            continue

        if pattern in text:
            print(f"\n# FILE: {path}")
            for i, line in enumerate(text.splitlines(), start=1):
                if pattern in line:
                    print(f"{i:4}: {line}")
    print("\n[DONE] search finished.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:\n  python search_in_project.py <root_dir> <pattern> [mask]\n")
        print("Example:\n  python search_in_project.py app/api/v1 \"db.commit\" \"**/*.py\"")
        sys.exit(1)

    root = sys.argv[1]
    pattern = sys.argv[2]
    mask = sys.argv[3] if len(sys.argv) >= 4 else "**/*.py"

    search(root, pattern, mask)
