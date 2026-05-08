import asyncio
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from fintoai.providers.csv_provider import CSVProvider

FIXTURE = Path(__file__).parent / "fixtures" / "sample_transactions.csv"


def test_fixture_exists():
    assert FIXTURE.exists(), "sample_transactions.csv must exist for tests"


def test_provider_raises_on_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        CSVProvider(tmp_path / "nope.csv")


def test_list_accounts_returns_one_account():
    provider = CSVProvider(FIXTURE)
    accounts = asyncio.run(provider.list_accounts())
    assert len(accounts) == 1
    assert accounts[0].provider == "csv"
    assert accounts[0].currency == "GBP"


def test_account_id_is_stable_across_instances():
    a = CSVProvider(FIXTURE)
    b = CSVProvider(FIXTURE)
    assert asyncio.run(a.list_accounts())[0].id == asyncio.run(b.list_accounts())[0].id


def test_list_transactions_returns_all_in_range():
    provider = CSVProvider(FIXTURE)
    accounts = asyncio.run(provider.list_accounts())
    txns = asyncio.run(
        provider.list_transactions(
            accounts[0].id,
            date_from=date(2026, 1, 1),
            date_to=date(2026, 12, 31),
        )
    )
    assert len(txns) == 10
    assert all(t.account_id == accounts[0].id for t in txns)


def test_list_transactions_filters_by_date():
    provider = CSVProvider(FIXTURE)
    accounts = asyncio.run(provider.list_accounts())
    txns = asyncio.run(
        provider.list_transactions(
            accounts[0].id,
            date_from=date(2026, 4, 10),
            date_to=date(2026, 4, 15),
        )
    )
    dates = [t.booking_date for t in txns]
    assert all(date(2026, 4, 10) <= d <= date(2026, 4, 15) for d in dates)


def test_amounts_are_decimal_not_float():
    provider = CSVProvider(FIXTURE)
    accounts = asyncio.run(provider.list_accounts())
    txns = asyncio.run(
        provider.list_transactions(accounts[0].id, date(2026, 1, 1), date(2026, 12, 31))
    )
    for t in txns:
        assert isinstance(t.amount, Decimal)


def test_unknown_account_id_returns_empty():
    provider = CSVProvider(FIXTURE)
    txns = asyncio.run(
        provider.list_transactions("not_a_real_id", date(2026, 1, 1), date(2026, 12, 31))
    )
    assert txns == []


def test_raw_payload_preserved():
    """The 'raw' field must contain the original CSV row for citation/audit."""
    provider = CSVProvider(FIXTURE)
    accounts = asyncio.run(provider.list_accounts())
    txns = asyncio.run(
        provider.list_transactions(accounts[0].id, date(2026, 1, 1), date(2026, 12, 31))
    )
    assert all("description" in t.raw for t in txns)


def test_health_check_passes():
    provider = CSVProvider(FIXTURE)
    assert asyncio.run(provider.health_check()) is True