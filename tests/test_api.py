"""Tests for the Luna API."""
import pytest
from fastapi import HTTPException
from luna.api import api
from luna.h5ad.h5ad_persist import H5adDb
from luna.db import cellular_annotation as ann
from luna.db import scatter_plot as sca
from luna.db.db_util import DbConnection


@pytest.fixture(scope="module", autouse=True)
def load_sample_data():
    """Fixture to ensure each test starts with a pre-populated database."""
    db_connection = DbConnection()
    db_connection.reset_database()
    file_name = "examples/tabula-muris-mini.h5ad"
    gene_list = ["Egfr", "P2ry12", "Serpina1c"]
    description = "Mini h5ad test file"
    url = "http://mini-h5ad-test-file.com"
    h5ad = H5adDb(file_name, description, url, gene_list)
    h5ad.persist_to_database()


def test_api():
    """Test the Luna API."""
    verify_buckets()
    verify_annotation_keys()
    verify_distinct_annotation_values()
    verify_annotation_values()
    verify_expression_data()
    verify_umap()
    verify_tsne()


def verify_buckets():
    res = api.get_buckets()
    assert len(res) == 1
    bucket0 = res[0]
    assert bucket0.name == "tabula-muris-mini.h5ad"
    assert bucket0.description == "Mini h5ad test file"
    assert bucket0.url == "http://mini-h5ad-test-file.com"


def verify_annotation_keys():
    res = api.get_annotation_list(1)
    assert len(res) == 12
    assert res[0].key == "cell_ontology_class"
    assert res[1].key == "clusters_from_manuscript"

    with pytest.raises(HTTPException):
        res = api.get_annotation_list(-1)


def verify_distinct_annotation_values():
    res = api.get_distinct_annotation_values(1)
    assert len(res) == 37
    assert res[0] == "astrocyte"
    assert res[1] == "B cell"

    with pytest.raises(HTTPException):
        res = api.get_distinct_annotation_values(-1)


def verify_annotation_values():
    res = api.get_annotation_values(1)
    assert len(res) == 100
    assert res[0] == "epidermal cell"
    assert res[1] == "endothelial cell"

    with pytest.raises(HTTPException):
        res = api.get_annotation_values(-1)


def verify_expression_data():
    res = api.get_expression_values(1, "Egfr")
    assert len(res) == 100
    assert res[0] == 0.6931472
    assert res[1] == 0.6931472

    with pytest.raises(HTTPException):
        res = api.get_expression_values(2, "Egfr")

    with pytest.raises(HTTPException):
        res = api.get_expression_values(1, "Pten")

def verify_umap():
    res = api.get_umap_coordinates(1)
    assert len(res) == 100
    assert res[0].x == -0.437479
    assert res[0].y == 13.087562

    with pytest.raises(HTTPException):
        res = api.get_umap_coordinates(2)

def verify_tsne():
    res = api.get_tsne_coordinates(1)
    assert len(res) == 100
    assert res[0].x == -43.720875
    assert res[0].y == -48.974918

    with pytest.raises(HTTPException):
        res = api.get_tsne_coordinates(2)
