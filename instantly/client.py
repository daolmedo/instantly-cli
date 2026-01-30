from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests

CONFIG_DIR = Path.home() / ".instantly"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_api_key() -> str:
    """Load API key from env var, falling back to config file."""
    key = os.environ.get("INSTANTLY_API_KEY", "")
    if key:
        return key
    if CONFIG_FILE.exists():
        data = json.loads(CONFIG_FILE.read_text())
        key = data.get("api_key", "")
        if key:
            return key
    return ""


def save_api_key(api_key: str) -> None:
    """Save API key to ~/.instantly/config.json."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps({"api_key": api_key}))


class InstantlyClient:
    BASE_URL = "https://api.instantly.ai"

    def __init__(self):
        self.api_key = load_api_key()
        if not self.api_key:
            print("Error: No API key found. Run 'instantly configure' or set INSTANTLY_API_KEY.", file=sys.stderr)
            sys.exit(1)
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })

    def _handle_response(self, resp: requests.Response) -> dict:
        if not resp.ok:
            print(f"Error {resp.status_code}: {resp.text}", file=sys.stderr)
            sys.exit(1)
        return resp.json()

    def get(self, path: str, params: dict | None = None) -> dict:
        resp = self.session.get(f"{self.BASE_URL}{path}", params=params)
        return self._handle_response(resp)

    def post(self, path: str, json: dict | None = None) -> dict:
        resp = self.session.post(f"{self.BASE_URL}{path}", json=json if json is not None else {})
        return self._handle_response(resp)

    def patch(self, path: str, json: dict | None = None) -> dict:
        resp = self.session.patch(f"{self.BASE_URL}{path}", json=json)
        return self._handle_response(resp)

    def delete(self, path: str, json: dict | None = None) -> dict:
        resp = self.session.delete(f"{self.BASE_URL}{path}", json=json)
        return self._handle_response(resp)
