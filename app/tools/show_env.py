# app/tools/show_env.py
from __future__ import annotations
import sys
from pathlib import Path
import site

def main() -> None:
    print("Python executable:", sys.executable)
    print("sys.prefix:", sys.prefix)
    print("CWD:", Path().resolve())
    print("\n--- sys.path ---")
    for p in sys.path:
        print("  ", p)
    print("\n--- site.getsitepackages() ---")
    for p in site.getsitepackages():
        print("  ", p)

if __name__ == "__main__":
    main()
