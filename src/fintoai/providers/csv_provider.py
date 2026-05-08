"""CSV-based BankProvider implementation.

Reads transactions from a CSV file. Useful for:
  - Local development before real bank integration
  - Users whose bank isn't supported by Open Banking
  - Reproducible test fixtures for the eval harness

Expected CSV schema (header row required):
    date,description,amount,currency,counterparty

  - date: ISO format (YYYY-MM-DD)
  - amount: signed decimal. Negative = debit, positive = credit.
  - counterparty: optional, may be empty
"""
from __future__ import annotations

import csv
import hashlib
from datetime import date
from decimal import Decimal
from pathlib import Path

from fintoai.providers.base import Account, BankProvider, Transaction


class CSVProvider(BankProvider):
    """Loads transactions from a CSV file on disk.

    A single CSV maps to a single Account. Account ID and name are
    derived from the file path so the same file always produces the
    same account ID across runs (important for storage/sync logic later).
    """

    def __init__(self, csv_path: Path | str, currency: str = "GBP") -> None:
        self.csv_path = Path(csv_path)
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV not found: {self.csv_path}")
        self._currency = currency
        self._account_id = self._derive_account_id(self.csv_path)
        self._account_name = self.csv_path.stem

    @staticmethod
    def _derive_account_id(path: Path) -> str:
        """Stable account ID derived from absolute path."""
        h = hashlib.sha256(str(path.resolve()).encode()).hexdigest()
        return f"csv_{h[:16]}"

    async def list_accounts(self) -> list[Account]:
        return [
            Account(
                id=self._account_id,
                name=self._account_name,
                iban=None,
                currency=self._currency,
                provider="csv",
            )
        ]

    async def list_transactions(
        self,
        account_id: str,
        date_from: date,
        date_to: date,
    ) -> list[Transaction]:
        if account_id != self._account_id:
            return []

        transactions: list[Transaction] = []
        with self.csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                txn_date = date.fromisoformat(row["date"].strip())
                if txn_date < date_from or txn_date > date_to:
                    continue
                txn = Transaction(
                    id=self._txn_id(row, i),
                    account_id=self._account_id,
                    booking_date=txn_date,
                    amount=Decimal(row["amount"].strip()),
                    currency=row.get("currency", self._currency).strip() or self._currency,
                    description=row["description"].strip(),
                    counterparty=(row.get("counterparty") or "").strip() or None,
                    raw=dict(row),
                )
                transactions.append(txn)
        return transactions

    @staticmethod
    def _txn_id(row: dict, line_no: int) -> str:
        """Deterministic transaction ID from row content + line number.

        Line number is included because two identical rows (same date,
        amount, description) are legitimately distinct transactions.
        """
        key = f"{row['date']}|{row['description']}|{row['amount']}|{line_no}"
        return hashlib.sha256(key.encode()).hexdigest()[:24]

    async def health_check(self) -> bool:
        return self.csv_path.exists() and self.csv_path.is_file()