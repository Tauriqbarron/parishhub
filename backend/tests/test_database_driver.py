"""The Postgres driver must match what requirements.txt installs (psycopg2-binary).

SQLAlchemy 2.1 changed the default driver for plain postgresql:// URLs to psycopg (v3), which
broke a production deploy with "No module named 'psycopg'". These tests fail if that happens again.
"""

import importlib

import pytest
from sqlalchemy.engine import make_url

from app.database import engine


def test_plain_postgresql_url_uses_psycopg2():
    assert (
        make_url("postgresql://user:pw@localhost/parish_db").get_dialect().driver
        == "psycopg2"
    )


def test_default_driver_is_installed():
    driver = make_url("postgresql://user:pw@localhost/parish_db").get_dialect().driver
    importlib.import_module(driver)


@pytest.mark.skipif(
    engine.dialect.name != "postgresql", reason="CI runs the suite on SQLite"
)
def test_app_engine_uses_psycopg2():
    assert engine.dialect.driver == "psycopg2"
