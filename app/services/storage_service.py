"""Storage service for invoices (in-memory with optional file persistence)."""
import json
import logging
from pathlib import Path
from typing import Dict, List

from app.models.invoice import Invoice
from app.exceptions import InvoiceNotFoundError

logger = logging.getLogger(__name__)


def _storage_path() -> Path:
    """Path to the JSON file for persisting invoices."""
    base = Path(__file__).resolve().parent.parent.parent
    data_dir = base / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir / "invoices.json"


class StorageService:
    """In-memory storage service for invoices, persisted to a JSON file."""

    def __init__(self, persist: bool = True):
        self._invoices: Dict[str, Invoice] = {}
        self._persist = persist
        self._path = _storage_path()
        if self._persist and self._path.exists():
            self._load()
        else:
            logger.info("Storage: using in-memory only (persist=%s, path=%s)", self._persist, self._path)

    def _load(self) -> None:
        """Load invoices from the JSON file."""
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data.get("invoices", []):
                inv = Invoice.model_validate(item)
                self._invoices[inv.id] = inv
            logger.info("Storage: loaded %s invoices from %s", len(self._invoices), self._path)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning("Storage: could not load from %s: %s", self._path, e)
            self._invoices = {}

    def _save_to_file(self) -> None:
        """Write all invoices to the JSON file."""
        if not self._persist:
            return
        try:
            invoices_list = [
                inv.model_dump(mode="json") for inv in self._invoices.values()
            ]
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump({"invoices": invoices_list}, f, indent=2)
        except Exception:
            pass

    def save(self, invoice: Invoice) -> Invoice:
        """Save an invoice."""
        self._invoices[invoice.id] = invoice
        self._save_to_file()
        return invoice

    def get(self, invoice_id: str) -> Invoice:
        """Get an invoice by ID."""
        if invoice_id not in self._invoices:
            keys = list(self._invoices.keys())[:5]
            logger.warning(
                "Storage: invoice_id %r not found. Have %s invoices: %s",
                invoice_id, len(self._invoices), keys,
            )
            print(f"[Storage] Invoice {invoice_id!r} not found. Stored ids: {keys}")  # visible in terminal
            raise InvoiceNotFoundError(f"Invoice {invoice_id} not found")
        return self._invoices[invoice_id]

    def get_all(self) -> List[Invoice]:
        """Get all invoices."""
        return list(self._invoices.values())

    def get_by_vendor(self, vendor_name: str) -> List[Invoice]:
        """Get all invoices for a specific vendor."""
        return [
            invoice
            for invoice in self._invoices.values()
            if invoice.parsed_data.vendor_name.lower() == vendor_name.lower()
        ]

    def update(self, invoice_id: str, **updates) -> Invoice:
        """Update an invoice."""
        invoice = self.get(invoice_id)
        for key, value in updates.items():
            setattr(invoice, key, value)
        self._save_to_file()
        return invoice

    def delete(self, invoice_id: str) -> bool:
        """Delete an invoice by ID."""
        if invoice_id not in self._invoices:
            raise InvoiceNotFoundError(f"Invoice {invoice_id} not found")
        del self._invoices[invoice_id]
        self._save_to_file()
        return True
