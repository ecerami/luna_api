"""Database Utilities."""
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, create_database, drop_database
from luna.db.base import Base


class DbConnection:
    """Datbase Connection with database engine and session objects."""

    # Pattern:  "postgresql+psycopg2://username:password@localhost/luna"
    DEFAULT_DB_CONNECT_STR = "postgresql+psycopg2://@localhost/luna"

    def __init__(self):
        """Construct a new Database Connection."""
        # If set, environment variable over-rides default.
        self.db_connect_str = os.getenv(
            "LUNA_DB_CONNECT", default=DbConnection.DEFAULT_DB_CONNECT_STR
        )

        # Create database and tables if they do not exist
        if not database_exists(self.db_connect_str):
            logging.info("Database does not exist.")
            create_database(self.db_connect_str)
        self._init_db_connections()

    def reset_database(self):
        """Reset the database and start with a clean slate."""
        logging.info("Dropping database.")
        drop_database(self.db_connect_str)
        self._create_database()

    def _create_database(self):
        logging.info("Creating database with all tables.")
        create_database(self.db_connect_str)
        Base.metadata.create_all(self.engine)
        self._init_db_connections()

    def _init_db_connections(self):
        self.engine = create_engine(self.db_connect_str)
        self.session = Session(bind=self.engine)
