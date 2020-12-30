"""Tests for the Luna API."""
import pytest
from fastapi import HTTPException
from luna.api import api
from luna.h5ad.h5ad_persist import H5adDb
from luna.db.db_util import DbConnection

BUCKET_SLUG = "tabula_muris_mini"
BUCKET_SLUG_DOES_NOT_EXIST = "hello_world"


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
    _verify_buckets()
    _verify_annotation_list()
    _verify_annotation_values()
    _verify_expression_data()
    _verify_umap()
    _verify_tsne()


def _verify_buckets():
    res = api.get_buckets()
    assert len(res) == 1
    bucket0 = res[0]
    assert bucket0.name == "tabula-muris-mini.h5ad"
    assert bucket0.slug == "tabula_muris_mini"
    assert bucket0.description == "Mini h5ad test file"
    assert bucket0.url == "http://mini-h5ad-test-file.com"


def _verify_annotation_list():
    res = api.get_annotation_list(BUCKET_SLUG)
    assert len(res) == 9
    assert res[0].label == "cell_ontology_class"
    assert res[1].label == "clusters_from_manuscript"

    with pytest.raises(HTTPException):
        res = api.get_annotation_list(BUCKET_SLUG_DOES_NOT_EXIST)


def _verify_annotation_values():
    res = api.get_annotation_values(BUCKET_SLUG, "cell_ontology_class")

    values_distinct = res.values_distinct
    assert len(values_distinct) == 37
    assert values_distinct[0] == "astrocyte"
    assert values_distinct[1] == "B cell"

    values_list = res.values_ordered
    assert len(values_list) == 100
    assert values_list[0] == "epidermal cell"
    assert values_list[1] == "endothelial cell"

    with pytest.raises(HTTPException):
        res = api.get_annotation_values(BUCKET_SLUG_DOES_NOT_EXIST, "XXX")


def _verify_expression_data():
    res = api.get_expression_values(BUCKET_SLUG, "Egfr")

    assert res.max_expression == 7.354609

    values_list = res.values_ordered
    assert len(values_list) == 100
    assert values_list[0] == 0.6931472
    assert values_list[1] == 0.6931472

    with pytest.raises(HTTPException):
        res = api.get_expression_values(BUCKET_SLUG_DOES_NOT_EXIST, "Egfr")

    with pytest.raises(HTTPException):
        res = api.get_expression_values(BUCKET_SLUG, "Pten")


def _verify_umap():
    res = api.get_umap_coordinates("tabula_muris_mini")
    assert len(res) == 100
    assert res[0].x == -0.437479
    assert res[0].y == 13.087562

    with pytest.raises(HTTPException):
        res = api.get_umap_coordinates("hello")


def _verify_tsne():
    res = api.get_tsne_coordinates(BUCKET_SLUG)
    assert len(res) == 100
    assert res[0].x == -43.720875
    assert res[0].y == -48.974918

    with pytest.raises(HTTPException):
        res = api.get_tsne_coordinates(BUCKET_SLUG_DOES_NOT_EXIST)
