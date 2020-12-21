"""Tests for DB Utility."""
import pytest
from luna.db.bucket import Bucket
from luna.db.db_util import DbConnection


@pytest.fixture(scope="module", autouse=True)
def reset_db():
    """Fixture to ensure each test starts with a clean slate database."""
    db_connection = DbConnection()
    db_connection.drop_database()


def test_db_util():
    """Test the DB Connection."""
    connection = DbConnection()
    bucket = Bucket("bucket1", "bucket_description", "http://bucket.com")
    connection.session.add(bucket)
    connection.session.commit()
    assert bucket.id == 1
