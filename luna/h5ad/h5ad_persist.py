"""Persist h5ad files to the database."""
import warnings
import anndata
import os
import logging
from sqlalchemy.orm import Session
from luna.db.bucket import Bucket
from luna.db.db_util import DbConnection
from luna.db.cellular_annotation import CellularAnnotation
from luna.db.cellular_annotation import CellularAnnotationType
from luna.db.scatter_plot import ScatterPlot, ScatterPlotType


class H5adDb:
    """Persist h5ad files to the database."""

    UMAP_KEY = "X_umap"
    TSNE_KEY = "X_tsne"

    def __init__(self, file_name, description, url, gene_list=[]):
        """
        Construct class with h5ad meta-data.

        If gene_list is empty, all genes will be imported.
        """
        # Ignore Future Warnings from anndata
        warnings.simplefilter(action="ignore", category=FutureWarning)

        self.h5ad_file_name = file_name
        self.description = description
        self.url = url

        self.base_file_name = os.path.basename(file_name)
        self.adata = anndata.read_h5ad(file_name)
        self.gene_list = gene_list

        # Set up the db connection and session
        self.db_connection = DbConnection()
        self.engine = self.db_connection.engine
        self.session = Session(bind=self.engine)

    def persist_to_database(self):
        """Persist to the database."""
        self._persist_bucket()
        self._persist_annotations()
        self._persist_scatter_plots()
        self._persist_x()

    def _persist_bucket(self):
        logging.info("Persisting bucket: %s" % self.base_file_name)
        self.bucket = Bucket(self.base_file_name, self.description, self.url)
        self.session.add(self.bucket)
        self.session.commit()
        logging.info("Got Bucket ID: %d" % self.bucket.id)

    def _persist_annotations(self):
        # Annotations are in .obs
        # obs is a pandas dataframe
        obs = self.adata.obs
        column_list = obs.columns
        for column_name in column_list:
            current_value_list = obs[column_name].to_list()
            current_value_set = set(current_value_list)
            if len(current_value_set) < 100:
                logging.info("Persisting annotations:  %s." % column_name)
                current_annotation = CellularAnnotation(
                    column_name,
                    CellularAnnotationType.OTHER,
                    current_value_list,
                    self.bucket.id,
                )
                self.session.add(current_annotation)
            else:
                logging.info("Skipping annotations:  %s." % column_name)
        self.session.commit()

    def _persist_scatter_plots(self):
        # Scatter plots are in .obsm
        obsm = self.adata.obsm

        self._persist_scatter_plot(obsm, H5adDb.UMAP_KEY, ScatterPlotType.UMAP)
        self._persist_scatter_plot(obsm, H5adDb.TSNE_KEY, ScatterPlotType.TSNE)

    def _persist_scatter_plot(self, obsm, obsm_key, scatter_plot_type):
        if obsm_key in obsm:
            logging.info("Persisting: %s." % obsm_key)
            scatter_plot = ScatterPlot(
                scatter_plot_type, obsm[obsm_key], self.bucket.id
            )
            self.session.add(scatter_plot)
            self.session.commit()

    def _persist_x(self):
        # Expression matrix is in .X
        # Gene symbols are in .var
        x = self.adata.X
        var = self.adata.var
        rows = x.shape[0]

        gene_index = self._create_gene_index_lookup(var)

        if self.gene_list is None or len(self.gene_list) == 0:
            self.gene_list = var.index

        for current_gene in self.gene_list:
            index = gene_index[current_gene]
            logging.info("Persisting: %s, index=%d." % (current_gene, index))
            slice = x[0:rows, index]
            current_annotation = CellularAnnotation(
                current_gene,
                CellularAnnotationType.GENE_EXPRESSION,
                slice,
                self.bucket.id,
            )
            self.session.add(current_annotation)
            self.session.commit()

    def _create_gene_index_lookup(self, var):
        gene_index = {}
        index_counter = 0
        for gene in var.index.to_list():
            gene_index[gene] = index_counter
            index_counter += 1
        return gene_index
