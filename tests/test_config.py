from app.config import Settings, get_settings, set_settings


def test_get_settings_cached() -> None:
    # Clear the cache
    get_settings.cache_clear()

    # Retrieve the settings
    s1 = get_settings()

    # Modify the settings
    set_settings(
        Settings(
            mongodb_url="mongodb://mongodb:27017",
            db_name="new_db",
            origins="https://example.com",
            host="0.0.0.0",
            port=9000,
            reload=True,
        )
    )

    # Retrieve the settings again
    s2 = get_settings()

    # Ensure the settings are cached
    assert s1 is s2


def test_set_settings() -> None:
    # Clear the cache
    get_settings.cache_clear()

    set_settings(
        Settings(
            mongodb_url="mongodb://mongodb:27017",
            db_name="new_db",
            origins="https://example.com",
            host="0.0.0.0",
            port=9000,
            reload=True,
        )
    )

    s = get_settings()

    assert s.mongodb_url == "mongodb://mongodb:27017"
    assert s.db_name == "new_db"
    assert s.origins == "https://example.com"
    assert s.host == "0.0.0.0"
    assert s.port == 9000
    assert s.reload is True
