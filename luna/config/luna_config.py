"""Luna Config."""
from configparser import ConfigParser


class LunaConfig:
    """Luna Config Class."""

    h5ad_file_name = None
    h5ad_description = None
    h5ad_url = None
    gene_list = None

    def __init__(self, config_file_name):
        """Create Config Object with specified configuration file."""
        cfg = ConfigParser()
        cfg.read(config_file_name)
        self.h5ad_file_name = cfg.get("h5ad", "file_name")
        self.h5ad_description = cfg.get("h5ad", "description")
        self.h5ad_url = cfg.get("h5ad", "url")

        if cfg.has_section("genes"):
            self.gene_list = cfg.get("genes", "gene_list", fallback=None)
            self.gene_list = [x.strip() for x in self.gene_list.split(",")]
        else:
            self.gene_list = None
