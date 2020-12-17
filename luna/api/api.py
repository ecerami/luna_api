"""
Luna API.

API is written via FastAPI.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from natsort import natsorted, ns
from luna.db.db_util import DbConnection
from luna.db import bucket
from luna.db import cellular_annotation as ann
from luna.db import scatter_plot as sca
from luna.db.base import DB_DELIM

app = FastAPI()


class Bucket(BaseModel):
    """Bucket Object."""

    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    id: int


class AnnotationKey(BaseModel):
    """Annotation Key Object."""

    key: str
    id: int


class Coordinate(BaseModel):
    """Coordinate Object."""

    x: float
    y: float


@app.get("/buckets", response_model=List[Bucket])
def get_buckets():
    """Get list of all buckets."""
    session = _init_db_connection()
    sql_bucket_list = session.query(bucket.Bucket).all()
    api_bucket_list = []
    for sql_bucket in sql_bucket_list:
        api_bucket = Bucket(
            name=sql_bucket.name,
            description=sql_bucket.description,
            url=sql_bucket.url,
            id=sql_bucket.id,
        )
        api_bucket_list.append(api_bucket)
    return api_bucket_list


@app.get("/annotations/{bucket_id}", response_model=List[AnnotationKey])
def get_annotation_list(bucket_id: int):
    """Get the annotation keys for the specified bucket."""
    session = _init_db_connection()

    record_list = (
        session.query(ann.CellularAnnotation.key, ann.CellularAnnotation.id)
        .filter_by(bucket_id=bucket_id, type=ann.CellularAnnotationType.OTHER)
        .order_by(ann.CellularAnnotation.key)
        .all()
    )

    if len(record_list) == 0:
        raise HTTPException(status_code=404, detail="Bucket not found.")

    annotation_list = []
    for record in record_list:
        current_annotation = AnnotationKey(key=record.key, id=record.id)
        annotation_list.append(current_annotation)
    return annotation_list


@app.get("/annotations/distinct/{annotation_id}", response_model=List[str])
def get_distinct_annotation_values(annotation_id: int):
    """Get the set of distinct values for the specified annotation ID."""
    session = _init_db_connection()

    record = (
        session.query(ann.CellularAnnotation.value_list)
        .filter_by(id=annotation_id)
        .first()
    )

    if record is None:
        raise HTTPException(status_code=404, detail="Annotation ID not found.")

    distinct_set = set()
    value_list = record.value_list.split(DB_DELIM)
    for value in value_list:
        value = value.strip()
        distinct_set.add(value)
    distinct_list = list(distinct_set)
    return natsorted(distinct_list, alg=ns.IGNORECASE)


@app.get("/annotations/all/{annotation_id}", response_model=List[str])
def get_annotation_values(annotation_id: int):
    """Get the list of all values for the specified annotation ID."""
    session = _init_db_connection()

    record = (
        session.query(ann.CellularAnnotation.value_list)
        .filter_by(id=annotation_id)
        .first()
    )

    if record is None:
        raise HTTPException(status_code=404, detail="Annotation ID not found.")

    response_list = []
    value_list = record.value_list.split(DB_DELIM)
    for current_value in value_list:
        current_value = current_value.strip()
        response_list.append(current_value)
    return response_list


@app.get("/expression/{bucket_id}/{gene_symbol}", response_model=List[float])
def get_expression_values(bucket_id: int, gene_symbol: str):
    """Get the expression data for the specified gene."""
    session = _init_db_connection()

    record = (
        session.query(ann.CellularAnnotation.value_list)
        .filter_by(bucket_id=bucket_id, key=gene_symbol)
        .first()
    )

    if record is None:
        raise HTTPException(status_code=404, detail="No data found.")

    response_list = []
    value_list = record.value_list.split(DB_DELIM)
    for current_value in value_list:
        current_value = float(current_value.strip())
        response_list.append(current_value)
    return response_list


@app.get("/umap/{bucket_id}", response_model=List[Coordinate])
def get_umap_coordinates(bucket_id: int):
    """Get the UMAP coordinates for the specified bucket."""
    session = _init_db_connection()

    record = (
        session.query(sca.ScatterPlot.coordinate_list)
        .filter_by(bucket_id=bucket_id, type=sca.ScatterPlotType.UMAP)
        .first()
    )

    if record is None:
        raise HTTPException(status_code=404, detail="No data found.")

    return _extract_coordinates(record)


@app.get("/tsne/{bucket_id}", response_model=List[Coordinate])
def get_tsne_coordinates(bucket_id: int):
    """Get the TSNE coordinates for the specified bucket."""
    session = _init_db_connection()

    record = (
        session.query(sca.ScatterPlot.coordinate_list)
        .filter_by(bucket_id=bucket_id, type=sca.ScatterPlotType.TSNE)
        .first()
    )

    if record is None:
        raise HTTPException(status_code=404, detail="No data found.")

    return _extract_coordinates(record)


def _extract_coordinates(record):
    response_list = []
    value_list = record.coordinate_list.split(DB_DELIM)
    for pair_str in value_list:
        if len(pair_str) > 0:
            parts = pair_str.split(",")
            current_value = Coordinate(x=float(parts[0]), y=float(parts[1]))
            response_list.append(current_value)
    return response_list


def _init_db_connection():
    db_connection = DbConnection()
    return db_connection.session
