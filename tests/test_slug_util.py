"""Tests for Slug Util."""
from luna.db.slug import SlugUtil


def test_sluggify():
    """Test the sluggify function."""
    slugger = SlugUtil()
    assert slugger.sluggify("Hello World!") == "hello_world"
    assert slugger.sluggify("Hello   World###!&&!") == "hello_world"
    assert slugger.sluggify("Hello___World###!&&!") == "hello_world"
    assert slugger.sluggify("tabula-muris.h5ad") == "tabula_muris"
