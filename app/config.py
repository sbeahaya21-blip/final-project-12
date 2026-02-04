"""Configuration management for the application."""
import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

# Load .env from project root so ERPNEXT_* variables can be set there
def _load_dotenv(path: Path) -> None:
    """Load KEY=VALUE lines from path into os.environ (no extra deps)."""
    if not path.exists():
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = value
    except Exception:
        pass


_env_path = Path(__file__).resolve().parent.parent / ".env"
_env_cwd = Path.cwd() / ".env"
for path in (_env_path, _env_cwd):
    if not path.exists():
        continue
    try:
        from dotenv import load_dotenv
        load_dotenv(path)
    except ImportError:
        _load_dotenv(path)
    break  # load only the first .env found


def _normalize_erpnext_base_url(url: str) -> str:
    """Use only scheme + host + port (no path). Frappe API is at {origin}/api/..."""
    if not url or not url.strip():
        return url
    url = url.strip().rstrip("/")
    try:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
    except Exception:
        return url


class Config:
    """Application configuration."""
    
    # ERPNext Configuration (strip whitespace so .env newlines don't break auth)
    _raw_base = (os.getenv('ERPNEXT_BASE_URL', 'https://your-instance.erpnext.com') or '').strip()
    ERPNEXT_BASE_URL: str = _normalize_erpnext_base_url(_raw_base)
    ERPNEXT_API_KEY: str = (os.getenv('ERPNEXT_API_KEY', '') or '').strip()
    ERPNEXT_API_SECRET: str = (os.getenv('ERPNEXT_API_SECRET', '') or '').strip()
    
    # Application Settings
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def validate_erpnext_config(cls) -> bool:
        """Validate that ERPNext configuration is set."""
        placeholder = 'https://your-instance.erpnext.com'
        return bool(
            cls.ERPNEXT_BASE_URL and
            cls.ERPNEXT_API_KEY and
            cls.ERPNEXT_API_SECRET and
            cls.ERPNEXT_BASE_URL.rstrip('/') != placeholder.rstrip('/')
        )
