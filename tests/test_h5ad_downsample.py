"""Tests for the Luna API."""
import os
import warnings
import anndata
from luna.h5ad.h5ad_downsample import H5adDownSample


def test_downsample():
    """Downsample the mini h5ad file even further to 10 cells and one gene."""
    path = "tests/data/"
    mini_h5ad = path + "tabula-muris-mini.h5ad"
    nano_h5ad = path + "tabula-muris-nano.h5ad"
    down_sampler = H5adDownSample(mini_h5ad, 10, ["Egfr"])
    down_sampler.save(nano_h5ad)
    _verify_nano_h5ad(nano_h5ad)
    os.remove(nano_h5ad)


def _verify_nano_h5ad(nano_h5ad):
    # Ignore Future Warnings from anndata
    warnings.simplefilter(action="ignore", category=FutureWarning)
    adata = anndata.read_h5ad(nano_h5ad)
    x = adata.X

    assert x.shape[0] == 10
    assert x.shape[1] == 1

    obsm = adata.obsm
    assert obsm["X_umap"][0][0] == -0.43747921610984725
    assert obsm["X_umap"][0][1] == 13.087562377179331

    obs_df = adata.obs
    obs_keys = obs_df.columns.to_list()
    assert len(obs_keys) == 12
