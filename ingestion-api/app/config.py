import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_ENV     = os.getenv('APP_ENV', 'local')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')

    DB_HOST     = os.getenv('DB_HOST', 'localhost')
    DB_PORT     = int(os.getenv('DB_PORT', 5432))
    DB_NAME     = os.getenv('DB_NAME', 'execution_db')
    DB_USER     = os.getenv('DB_USER', 'user_exec')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    # FIX: sslmode was missing from Config; db.py reads it directly from env,
    #      but Config should expose it for completeness and testability.
    DB_SSLMODE  = os.getenv('DB_SSLMODE', 'prefer')

    def db_config(self) -> dict:
        """Return a dict suitable for psycopg2.connect(**cfg.db_config())."""
        return {
            'host':     self.DB_HOST,
            'port':     self.DB_PORT,
            'dbname':   self.DB_NAME,
            'user':     self.DB_USER,
            'password': self.DB_PASSWORD,
            'sslmode':  self.DB_SSLMODE,
        }
