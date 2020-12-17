"""Cellular Annotation."""
from luna.db.base import Base, DB_DELIM
from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum
import enum


class CellularAnnotationType(enum.Enum):
    """Cellular Annotation Type."""

    GENE_EXPRESSION = "GENE_EXPRESSION"
    OTHER = "OTHER"


class CellularAnnotation(Base):
    """Cellular Annotation ORM Class."""

    __tablename__ = "cellular_annotation"

    id = Column(Integer, primary_key=True)
    key = Column(String)
    type = Column(Enum(CellularAnnotationType))
    value_list = Column(String)
    bucket_id = Column(Integer, ForeignKey("bucket.id"))
    bucket = relationship("Bucket", backref="cellular_annotation_list")

    def __init__(self, key, type, value_list, bucket_id):
        """Create new CellularAnnotation Object."""
        self.key = key
        self.type = type
        self.value_list = DB_DELIM.join(map(str, value_list))
        self.bucket_id = bucket_id

    def __repr__(self):
        """Get CellularAnnotation Summary."""
        token_list = self.coordinate_list.split(DB_DELIM)
        return "<CellularAnnotation(%s, type=%s, vector of %d elements)>" % (
            self.key,
            self.annotation_type,
            len(token_list),
        )
