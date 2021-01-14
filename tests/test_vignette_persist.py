"""Tests for Vignette Validator."""
from luna.db import vignette
import pytest
from luna.db.bucket import Bucket
from luna.vignette.vignette_persist import VignetteDb
from luna.db.db_util import DbConnection


@pytest.fixture()
def reset_db():
    """Fixture to ensure each test starts with a clean slate database."""
    db_connection = DbConnection()
    db_connection.reset_database()


def test_valid_bucket():
    """Test JSON with Valid Bucket Slug."""
    # Add a bucket, so that we can refer to it in the vignettes
    bucket = Bucket("tabula_muris", "Description", "URL")
    db_connection = DbConnection()
    session = db_connection.session
    session.add(bucket)
    session.commit()

    # Add the Vignettes
    vignette_file = "tests/data/vignette_valid.json"
    vignette_db = VignetteDb(vignette_file)
    vignette_db.persist_to_database()

    # Verify that the Vignettes were added
    record_list = session.query(vignette.Vignette).all()
    assert len(record_list) == 1
    record = record_list[0]
    assert record.json.startswith('{"bucket_slug": "tabula_muris"')
    assert repr(record).startswith("<Vignettes(")
