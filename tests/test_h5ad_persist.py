"""Tests for Persisting h5ad file to the database."""
import pytest
from luna.db import bucket
from luna.h5ad.h5ad_persist import H5adDb
from luna.db import cellular_annotation as ann
from luna.db import scatter_plot as sca
from luna.db.db_util import DbConnection


@pytest.fixture()
def reset_db():
    """Fixture to ensure each test starts with a clean slate database."""
    db_connection = DbConnection()
    db_connection.reset_database()


def test_h5ad_persist_select_genes(reset_db):
    """Test Persisting of mini h5ad file, select genes to the database."""
    slug = "tabula_muris_mini"
    file_name = "examples/tabula-muris-mini.h5ad"
    gene_list = ["Egfr", "P2ry12", "Serpina1c"]
    description = "Mini h5ad test file"
    url = "http://mini-h5ad-test-file.com"
    h5ad = H5adDb(slug, file_name, description, url, gene_list)
    h5ad.persist_to_database()
    db_connection = DbConnection()
    session = db_connection.session
    bucket_id = verify_bucket(session)
    annotation_id = verify_annotation_keys(session, bucket_id)
    verify_cell_ontology_values(session, annotation_id)
    verify_umap(session, bucket_id)
    verify_gene_expression(session, bucket_id)
    session.close()


def test_h5ad_persist_all_genes(reset_db):
    """Test Persisting of mini h5ad file, all genes to the database."""
    slug = "tabula_muris_mini"
    file_name = "examples/tabula-muris-mini.h5ad"
    description = "Mini h5ad test file"
    url = "http://mini-h5ad-test-file.com"
    h5ad = H5adDb(slug, file_name, description, url)
    h5ad.persist_to_database()
    db_connection = DbConnection()
    session = db_connection.session
    bucket_id = verify_bucket(session)
    verify_gene_expression(session, bucket_id)
    session.close()


def verify_bucket(session):
    """Verify Bucket Contents."""
    bucket_list = session.query(bucket.Bucket).all()
    assert len(bucket_list) == 1
    first_bucket = bucket_list[0]
    assert first_bucket.name == "tabula-muris-mini.h5ad"
    assert first_bucket.description == "Mini h5ad test file"
    assert first_bucket.url == "http://mini-h5ad-test-file.com"
    assert repr(first_bucket).startswith("<Bucket(tabula_muris_mini")
    return first_bucket.id


def verify_annotation_keys(session, bucket_id):
    """Verify cellular annotations keys."""
    record_list = (
        session.query(ann.CellularAnnotation.slug, ann.CellularAnnotation.id)
        .filter_by(bucket_id=bucket_id, type=ann.CellularAnnotationType.OTHER)
        .order_by(ann.CellularAnnotation.slug)
        .all()
    )
    assert len(record_list) == 9
    assert record_list[0][0] == "cell_ontology_class"
    assert record_list[8][0] == "tissue"
    return record_list[0][1]


def verify_umap(session, bucket_id):
    """Verify UMAP Coordinates."""
    record = (
        session.query(sca.ScatterPlot)
        .filter_by(bucket_id=bucket_id, type=sca.ScatterPlotType.UMAP)
        .first()
    )
    target = "-0.437479,13.087562|-0.407288,2.570779|-1.995685,17.068936|"
    assert record.coordinate_list.startswith(target)
    assert repr(record).startswith("<ScatterPlot(vector of 101 elements)>")


def verify_gene_expression(session, bucket_id):
    """Verify Gene Expression Data."""
    record = (
        session.query(ann.CellularAnnotation.value_list)
        .filter_by(bucket_id=bucket_id, slug="egfr")
        .first()
    )
    target = "0.6931472|0.6931472|4.1136827|0.6931472|0.6931472|0.6931472"
    assert record.value_list.startswith(target)


def verify_cell_ontology_values(session, a_id):
    """Verify cell ontology values."""
    record = session.query(ann.CellularAnnotation).filter_by(id=a_id).first()
    target = "epidermal cell|endothelial cell|basal cell|endothelial"
    assert record.value_list.startswith(target)
    assert repr(record).startswith("<CellularAnnotation(cell_ontology_class")
