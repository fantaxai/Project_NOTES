#!/usr/bin/env python
"""
Скрипт для запуска инструментов форматирования.
"""

import subprocess
import sys


def run_cmd(cmd):
    print(f"\n>>> {cmd}")
    print("-" * 50)
    return subprocess.run(cmd, shell=True).returncode == 0


def main():
    print("\n" + "=" * 50)
    print("CODE FORMATTING")
    print("=" * 50)

    if "--fix" in sys.argv:
        print("\n--- FIXING ---")
        run_cmd("python -m isort .")
        run_cmd("python -m black .")
        print("\n>>> Done!")
        return

    print("\n--- CHECKING ---")
    ok1 = run_cmd("python -m isort . --check-only --diff")
    ok2 = run_cmd("python -m black . --check --diff")

    print("\n" + "=" * 50)
    if ok1 and ok2:
        print(">>> ALL OK!")
    else:
        print(">>> Run 'python lint.py --fix' to fix")
        sys.exit(1)


if __name__ == "__main__":
    main()
