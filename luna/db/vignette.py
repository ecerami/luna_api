"""Vignette object for storing a multiple vignettes."""
from luna.db.slug import SlugUtil
from luna.db.base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class Vignette(Base):
    """Vignette ORM Class."""

    __tablename__ = "vignette"

    id = Column(Integer, primary_key=True)
    bucket_id = Column(Integer, ForeignKey("bucket.id"))
    bucket = relationship("Bucket", backref="vignette_list")
    json = Column(String)

    def __init__(self, bucket_id, json):
        """Create Vignette Object."""
        self.bucket_id = bucket_id
        self.json = json

    def __repr__(self):
        """Get Vignettes Summary."""
        return "<Vignettes(%s)>" % (self.bucket_id)
