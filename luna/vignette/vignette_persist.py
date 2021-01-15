"""Persist vignettes to the database."""
import logging
import json
from jsonschema.exceptions import ValidationError
from sqlalchemy.orm import Session
from luna.db.vignette import Vignette
from luna.db.db_util import DbConnection
from luna.db import bucket


class VignetteDb:
    """Persist vignettes to the database."""

    def __init__(self, vingette_file_name):
        """Create new VignetteDB Instance."""
        self.vignette_file_name = vingette_file_name

        # Set up the db connection and session
        self.db_connection = DbConnection()
        self.engine = self.db_connection.engine
        self.session = Session(bind=self.engine)

    def persist_to_database(self):
        """Persist to the database."""
        with open(self.vignette_file_name) as f:
            vignette_json = json.load(f)
            bucket_slug = vignette_json["bucket_slug"]
            bucket_id = self._get_bucket_id(bucket_slug)
            vignette = Vignette(bucket_id, json.dumps(vignette_json))
            self.session.add(vignette)
            self.session.commit()
            logging.info("Got Vignette ID: %d" % vignette.id)
            self.session.close()

    def _get_bucket_id(self, bucket_slug):
        record = self.session.query(bucket.Bucket).filter_by(slug=bucket_slug)
        record = record.first()
        if record:
            return record.id
        else:
            raise ValidationError("Bucket not found:  " + bucket_slug)
