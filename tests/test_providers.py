def test_bank_provider_is_abstract():
    from fintoai.providers import BankProvider
    import pytest

    with pytest.raises(TypeError):
        BankProvider()
