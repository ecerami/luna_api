"""
Luna API.

API is written via FastAPI.
"""
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import List, Optional
from natsort import natsorted, ns
from luna.db.db_util import DbConnection
from luna.db import bucket
from luna.db import vignette
from luna.db import cellular_annotation as ann
from luna.db import scatter_plot as sca
from luna.db.base import DB_DELIM
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Bucket(BaseModel):
    """Bucket Object."""

    slug: str
    name: str
    description: Optional[str] = None
    url: Optional[str] = None


class Vignettes(BaseModel):
    """Vignettes Object."""

    content: str


class Annotation(BaseModel):
    """Annotation Object."""

    slug: str
    label: str


class AnnotationBundle(Annotation):
    """Annotation Bundle Object."""

    values_distinct: List[str]
    values_ordered: List[str]


class ExpressionBundle(BaseModel):
    """Expression Bundle Object."""

    gene: str
    max_expression: float
    values_ordered: List[float]


class Coordinate(BaseModel):
    """Coordinate Object."""

    x: float
    y: float


@app.get("/buckets", response_model=List[Bucket])
def get_buckets():
    """Get list of all data buckets."""
    session = _init_db_connection()
    try:
        sql_bucket_list = session.query(bucket.Bucket).all()
        api_bucket_list = []
        for sql_bucket in sql_bucket_list:
            api_bucket = Bucket(
                name=sql_bucket.name,
                description=sql_bucket.description,
                url=sql_bucket.url,
                slug=sql_bucket.slug,
            )
            api_bucket_list.append(api_bucket)
        return api_bucket_list
    finally:
        session.close()


@app.get("/annotation_list/{bucket_slug}", response_model=List[Annotation])
def get_annotation_list(bucket_slug: str):
    """Get the list of annotations for the specified bucket."""
    session = _init_db_connection()
    target_type = ann.CellularAnnotationType.OTHER
    try:
        bucket_id = _get_bucket_id(session, bucket_slug)
        record_list = (
            session.query(ann.CellularAnnotation)
            .filter_by(bucket_id=bucket_id, type=target_type)
            .order_by(ann.CellularAnnotation.slug)
            .all()
        )

        if len(record_list) == 0:
            raise HTTPException(status_code=404, detail="No annotations.")

        annotation_list = []
        for r in record_list:
            current_annotation = Annotation(label=r.label, slug=r.slug)
            annotation_list.append(current_annotation)
        return annotation_list
    finally:
        session.close()


@app.get(
    "/annotation/{bucket_slug}/{annotation_slug}",
    response_model=AnnotationBundle,
)
def get_annotation_values(bucket_slug: str, annotation_slug: str):
    """Get the list of all values for the specified annotation."""
    session = _init_db_connection()
    try:
        bucket_id = _get_bucket_id(session, bucket_slug)
        record = session.query(ann.CellularAnnotation)
        record = record.filter_by(
            bucket_id=bucket_id, slug=annotation_slug
        ).first()

        if record is None:
            raise HTTPException(status_code=404, detail="ID not found.")

        value_list = record.value_list.split(DB_DELIM)
        distinct_list = list({value.strip() for value in value_list})
        distinct_list = natsorted(distinct_list, alg=ns.IGNORECASE)

        current_annotation = AnnotationBundle(
            label=record.label,
            slug=record.slug,
            values_distinct=distinct_list,
            values_ordered=value_list,
        )
        return current_annotation
    finally:
        session.close()


@app.get("/expression/{bucket_slug}/{gene}", response_model=ExpressionBundle)
def get_expression_values(bucket_slug: str, gene: str):
    """Get the expression data for the specified gene."""
    gene = gene.lower()
    session = _init_db_connection()
    try:
        bucket_id = _get_bucket_id(session, bucket_slug)
        record = (
            session.query(ann.CellularAnnotation.value_list)
            .filter_by(bucket_id=bucket_id, slug=gene)
            .first()
        )

        if record is None:
            raise HTTPException(status_code=404, detail="No data found.")

        value_list = record.value_list.split(DB_DELIM)
        expression_bundle = ExpressionBundle(
            gene=gene,
            max_expression=max(value_list),
            values_ordered=value_list,
        )
        return expression_bundle
    finally:
        session.close()


@app.get("/umap/{bucket_slug}", response_model=List[Coordinate])
def get_umap_coordinates(bucket_slug: str):
    """Get the UMAP coordinates for the specified bucket."""
    session = _init_db_connection()
    try:
        bucket_id = _get_bucket_id(session, bucket_slug)
        record = (
            session.query(sca.ScatterPlot.coordinate_list)
            .filter_by(bucket_id=bucket_id, type=sca.ScatterPlotType.UMAP)
            .first()
        )

        if record is None:
            raise HTTPException(status_code=404, detail="No data found.")

        return _extract_coordinates(record)
    finally:
        session.close()


@app.get("/tsne/{bucket_slug}", response_model=List[Coordinate])
def get_tsne_coordinates(bucket_slug: str):
    """Get the TSNE coordinates for the specified bucket."""
    session = _init_db_connection()
    try:
        bucket_id = _get_bucket_id(session, bucket_slug)
        record = (
            session.query(sca.ScatterPlot.coordinate_list)
            .filter_by(bucket_id=bucket_id, type=sca.ScatterPlotType.TSNE)
            .first()
        )

        if record is None:
            raise HTTPException(status_code=404, detail="No data found.")

        return _extract_coordinates(record)
    finally:
        session.close()


@app.get("/vignettes/{bucket_slug}")
def get_vignettes(bucket_slug: str):
    """Get all Vignettes for the specified bucket."""
    session = _init_db_connection()
    try:
        bucket_id = _get_bucket_id(session, bucket_slug)
        record = (
            session.query(vignette.Vignette)
            .filter_by(bucket_id=bucket_id)
            .first()
        )

        if record is None:
            raise HTTPException(status_code=404, detail="No data found.")
        return Response(content=record.json, media_type="application/json")
    finally:
        session.close()


def _get_bucket_id(session, bucket_slug):
    record = session.query(bucket.Bucket).filter_by(slug=bucket_slug).first()
    if record:
        return record.id
    else:
        raise HTTPException(status_code=404, detail="Bucket not found")


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
