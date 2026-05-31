#!/usr/bin/env python3
"""bootstrap.py

Cross-platform bootstrap to create a `.venv` virtual environment in the
workspace and install packages from `requirements.txt`.

Usage:
  py -3 bootstrap.py    # Windows with py launcher
  python3 bootstrap.py  # Unix-like or if python is on PATH
"""
import subprocess
import sys
import venv
from pathlib import Path

root = Path(__file__).parent.resolve()
venv_dir = root / ".venv"

def create_venv():
    if not venv_dir.exists():
        print("Creating virtual environment in .venv...")
        venv.create(venv_dir, with_pip=True)
    else:
        print(".venv already exists")

def get_venv_python():
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    else:
        return venv_dir / "bin" / "python"

def run(cmd):
    print('>',' '.join(cmd))
    subprocess.check_call(cmd)

def main():
    create_venv()
    py = get_venv_python()
    if not py.exists():
        print("Error: python executable not found in venv:", py)
        sys.exit(1)

    print("Upgrading pip...")
    run([str(py), "-m", "pip", "install", "--upgrade", "pip"])

    req = root / "requirements.txt"
    if req.exists():
        print("Installing requirements.txt...")
        run([str(py), "-m", "pip", "install", "-r", str(req)])
    else:
        print("No requirements.txt found, skipping.")

    print("Done. Activate the venv:")
    if sys.platform == "win32":
        print("  PowerShell: .\\.venv\\Scripts\\Activate.ps1")
    else:
        print("  Bash: source .venv/bin/activate")

if __name__ == '__main__':
    main()
