def test_settings_loads_with_defaults(monkeypatch, tmp_path):
    """Settings should load even with no .env file present."""
    monkeypatch.chdir(tmp_path)  # somewhere with no .env
    from fintoai.config import Settings

    s = Settings()
    assert s.database_url.startswith("sqlite:///")
    assert s.log_level == "INFO"


def test_settings_reads_env_vars(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GOCARDLESS_SECRET_ID", "test-id-123")
    from fintoai.config import Settings

    s = Settings()
    assert s.gocardless_secret_id == "test-id-123"


def test_get_settings_is_cached():
    from fintoai.config import get_settings

    assert get_settings() is get_settings()