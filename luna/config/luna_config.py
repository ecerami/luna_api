"""Luna Config."""
import json
from jsonschema import validate

class LunaConfig:
    """Luna Config Class."""

    h5ad_file_name = None
    h5ad_description = None
    h5ad_url = None
    gene_list = None

    def __init__(self, config_file_name):
        """Create Config Object with specified configuration JSON."""

        with open("schemas/luna.json") as f:
            schema_json = json.load(f)

        with open(config_file_name) as f:
            luna_json = json.load(f)

        # In the event of a schema error, validate raises a
        # jsonschema.exceptions.ValidationError
        validate(instance=luna_json, schema=schema_json)

        if "h5ad" in luna_json:
            h5ad = luna_json["h5ad"]        
            self.h5ad_file_name = h5ad["file_name"]
            self.h5ad_description = h5ad["description"]
            self.h5ad_url = h5ad["url"]

        if "genes" in luna_json:
            self.gene_list = luna_json["genes"]
        else:
            self.gene_list = None
