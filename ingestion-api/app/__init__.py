"""ingestion-api application package.

Importing from here lets gunicorn, tests, and run_dbt use a consistent path:

    gunicorn "app:create_app()"   (if using factory pattern)
    from app import app           (current pattern)
"""
from .app import app  # noqa: F401  – re-export for external callers

__all__ = ["app"]
