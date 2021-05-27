"""Luna Config."""
import json
from jsonschema import validate


class LunaConfig:
    """Luna Config Class."""

    h5ad_file_name = None
    h5ad_description = None
    h5ad_url = None
    gene_list = None
    slug = None

    def __init__(self, config_file_name):
        """Create Config Object with specified configuration JSON."""
        with open("schemas/luna.json") as f:
            schema_json = json.load(f)

        with open(config_file_name) as f:
            luna_json = json.load(f)

        # In the event of a schema error, validate raises a
        # jsonschema.exceptions.ValidationError
        validate(instance=luna_json, schema=schema_json)

        if "bucket" in luna_json:
            bucket = luna_json["bucket"]
            self.h5ad_file_name = bucket["file_name"]
            self.h5ad_description = bucket["description"]
            self.h5ad_url = bucket["url"]
            self.slug = bucket["slug"]

            if "genes" in bucket:
                self.gene_list = bucket["genes"]
            else:
                self.gene_list = None
