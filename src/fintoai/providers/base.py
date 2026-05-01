"""Abstract interface for bank data providers.

All bank integrations (GoCardless, Plaid, CSV imports, mocks) must
implement this interface. The agent layer never talks to a provider
directly — it talks to this contract.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True)
class Account:
    id: str
    name: str
    iban: str | None
    currency: str
    provider: str  # "gocardless", "csv", etc.


@dataclass(frozen=True)
class Transaction:
    id: str
    account_id: str
    booking_date: date
    amount: Decimal  # negative = debit, positive = credit
    currency: str
    description: str
    counterparty: str | None
    raw: dict  # original provider payload, for audit/debugging


class BankProvider(ABC):
    """Read-only interface to a bank data source."""

    @abstractmethod
    async def list_accounts(self) -> list[Account]:
        """Return all accounts the user has authorised."""

    @abstractmethod
    async def list_transactions(
        self,
        account_id: str,
        date_from: date,
        date_to: date,
    ) -> list[Transaction]:
        """Return transactions for an account in a date range."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the provider is reachable and authenticated."""