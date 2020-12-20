import pytest
import configparser
from luna.config.luna_config import LunaConfig

CONFIG_PATH = "tests/data/"

def test_valid_config_file1():
  config = LunaConfig(CONFIG_PATH + "tabula_muris_select_genes.ini")
  assert (config.h5ad_file_name == "examples/tabula-muris.h5ad")
  assert (config.h5ad_description.startswith("Tabula Muris is a compendium"))
  assert (config.h5ad_url == "https://tabula-muris.ds.czbiohub.org/")
  gene_list = config.gene_list
  assert len(gene_list) == 3
  assert gene_list[0] == "Egfr"

def test_valid_config_file2():
  config = LunaConfig(CONFIG_PATH + "tabula_muris_all_genes.ini")
  assert (config.h5ad_file_name == "examples/tabula-muris.h5ad")
  assert (config.h5ad_description.startswith("Tabula Muris is a compendium"))
  assert (config.h5ad_url == "https://tabula-muris.ds.czbiohub.org/")
  assert config.gene_list == None

def test_invalid_config():
  with pytest.raises(configparser.NoSectionError):
    config = LunaConfig(CONFIG_PATH + "tabula_muris_broken.ini")
