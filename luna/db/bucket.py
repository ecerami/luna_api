"""Bucket object for storing a collection of cells."""

from luna.db.base import Base
from sqlalchemy import Column, Integer, String


class Bucket(Base):
    """Bucket ORM Class."""

    __tablename__ = "bucket"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    url = Column(String)

    def __init__(self, name, description=None, url=None):
        """Create Bucket Object."""
        self.name = name
        self.description = description
        self.url = url

    def __repr__(self):
        """Get bucket summary."""
        return "<Bucket(%s, %s)>" % (self.name, self.description)
