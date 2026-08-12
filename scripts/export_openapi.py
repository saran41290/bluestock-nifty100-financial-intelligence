"""
scripts/export_openapi.py

Exports OpenAPI 3.0 specification to docs/openapi.json and Postman Collection JSON.
"""

import json
from pathlib import Path
from src.api.main import app

DOCS_DIR = Path("docs")
DOCS_DIR.mkdir(exist_ok=True)

# 1. Export OpenAPI spec
openapi_data = app.openapi()
openapi_path = DOCS_DIR / "openapi.json"
with open(openapi_path, "w", encoding="utf-8") as f:
    json.dump(openapi_data, f, indent=2)

print(f"Exported OpenAPI spec to {openapi_path}")

# 2. Export Postman Collection JSON
postman_items = []
for path, methods in openapi_data.get("paths", {}).items():
    for method, spec in methods.items():
        postman_items.append({
            "name": spec.get("summary", path),
            "request": {
                "method": method.upper(),
                "header": [],
                "url": {
                    "raw": "http://localhost:8000" + path,
                    "protocol": "http",
                    "host": ["localhost"],
                    "port": "8000",
                    "path": [p for p in path.split("/") if p]
                },
                "description": spec.get("description", "")
            }
        })

postman_collection = {
    "info": {
        "name": "Nifty 100 Financial Intelligence API",
        "description": "Postman collection for all 16 FastAPI endpoints.",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": postman_items
}

postman_path = DOCS_DIR / "postman_collection.json"
with open(postman_path, "w", encoding="utf-8") as f:
    json.dump(postman_collection, f, indent=2)

print(f"Exported Postman collection to {postman_path}")
