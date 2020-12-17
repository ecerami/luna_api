"""Downsample an h5ad file."""
import warnings
import anndata
import numpy as np
import logging


class H5adDownSample:
    """
    Downsample an h5ad file to a smaller size.

    Used to create smaller h5ad files that can you used by unit tests.
    """

    def __init__(self, file_name, num_cells, gene_list=[]):
        """Construct class with h5ad meta-data."""
        # Ignore Future Warnings from anndata
        warnings.simplefilter(action="ignore", category=FutureWarning)

        self.file_name = file_name
        self.gene_list = gene_list
        self.num_cells = num_cells

    def save(self, downsample_file_name):
        """Save newly downsampled h5ad file to specified file."""
        adata = anndata.read_h5ad(self.file_name)
        x = adata.X
        gene_index = self._create_gene_index_lookup(adata.var)
        num_rows = min(x.shape[0], self.num_cells)
        logging.info("Restricting new file to %d cells." % num_rows)
        logging.info("Restricting new file to %d genes." % len(self.gene_list))

        d_x = self._get_downsampled_x(x, self.gene_list, gene_index, num_rows)
        d_var = adata.var.loc[self.gene_list]
        d_obs = adata.obs.head(num_rows)
        d_obsm = self._get_downsampled_obsm(adata.obsm, num_rows)
        new_h5ad = anndata.AnnData(X=d_x, var=d_var, obs=d_obs, obsm=d_obsm)
        new_h5ad.write_h5ad(downsample_file_name)

    def _get_downsampled_x(self, x, gene_list, gene_index, num_rows):
        new_x = []
        for gene in gene_list:
            index = gene_index[gene]
            logging.info("Extracting: %s, index=%d." % (gene, index))
            new_x.append(x[0:num_rows, index])
        new_x = np.column_stack(new_x)
        return new_x

    def _get_downsampled_obsm(self, obsm, num_rows):
        new_obsm = {}
        for key in obsm.keys():
            logging.info("Extracting: %s." % key)
            new_obsm[key] = obsm[key][0:num_rows]
        return new_obsm

    def _create_gene_index_lookup(self, var):
        gene_index = {}
        index_counter = 0
        for gene in var.index.to_list():
            gene_index[gene] = index_counter
            index_counter += 1
        return gene_index
