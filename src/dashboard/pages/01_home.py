"""
01_home.py - Home Screen wrapper
"""
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[3]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

with open(root / "pages" / "01_home.py", encoding="utf-8") as f:
    exec(f.read())
