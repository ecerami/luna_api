"""ScatterPlot object for storing X,Y coordinates."""
from luna.db.base import Base, DB_DELIM
from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum
import enum


class ScatterPlotType(enum.Enum):
    """ScatterPlot Type."""

    UMAP = "UMAP"
    TSNE = "TSNE"


class ScatterPlot(Base):
    """Scatter Plot ORM Class."""

    __tablename__ = "scatter_plot"

    id = Column(Integer, primary_key=True)
    type = Column(Enum(ScatterPlotType))
    coordinate_list = Column(String)
    bucket_id = Column(Integer, ForeignKey("bucket.id"))
    bucket = relationship("Bucket", backref="scatter_plot_list")

    def __init__(self, type, value_list, bucket_id):
        """Create new ScatterPlot Object."""
        self.type = type

        self.coordinate_list = ""
        for coord in value_list:
            self.coordinate_list += "%f,%f%s" % (coord[0], coord[1], DB_DELIM)
        self.bucket_id = bucket_id

    def __repr__(self):
        """Get Scatter Plot Summary."""
        token_list = self.coordinate_list.split(DB_DELIM)
        return "<ScatterPlot(vector of %d elements)>" % (
            len(token_list),
        )
