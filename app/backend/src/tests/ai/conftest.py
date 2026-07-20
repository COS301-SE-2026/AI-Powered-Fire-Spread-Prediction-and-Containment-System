import sys
from pathlib import Path

# Points to app/backend/src and app/ml — skips the parent conftest
# that loads the full backend app and requires minio/db dependencies
root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(root / "app" / "backend" / "src"))
sys.path.insert(0, str(root / "app" / "ml"))
