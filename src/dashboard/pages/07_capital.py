import sys
from pathlib import Path
root = Path(__file__).resolve().parents[3]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

with open(root / "pages" / "07_capital.py", encoding="utf-8") as f:
    exec(f.read())
