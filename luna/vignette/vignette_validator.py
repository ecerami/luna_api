"""Validate vignette JSON document."""
import json
from jsonschema import validate


class VignetteValidator:
    """Vignette File JSON Validator."""

    def __init__(self, vingette_file_name):
        """Create new VignetteValidator Instance."""
        self.vignette_file_name = vingette_file_name

    def validate(self):
        "Validate against vignette schema."
        with open(self.vignette_file_name) as f:
            vignette_json = json.load(f)
        with open("schemas/vignette_schema.json") as f:
            schema_json = json.load(f)

        # In the event of a schema error, validate raise a
        # jsonschema.exceptions.ValidationError
        validate(instance=vignette_json, schema=schema_json)
