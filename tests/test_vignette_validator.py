"""Tests for Vignette Validator."""
import pytest
from jsonschema.exceptions import ValidationError
from luna.vignette.vignette_validator import VignetteValidator


def test_invalid_json():
    """Test invalid JSON."""
    # Validation Error Expected
    validator = VignetteValidator("tests/data/vignette_invalid1.json")
    with pytest.raises(ValidationError) as validation_error:
        validator.validate()
    exception_msg = validation_error.value.args[0]
    assert exception_msg == "'slug' is a required property"

    # Validation Error Expected
    validator = VignetteValidator("tests/data/vignette_invalid2.json")
    with pytest.raises(ValidationError) as validation_error:
        validator.validate()
    exception_msg = validation_error.value.args[0]
    assert exception_msg == "'slug' is a required property"

    # Validation Error Expected
    validator = VignetteValidator("tests/data/vignette_invalid3.json")
    with pytest.raises(ValidationError) as validation_error:
        validator.validate()
    exception_msg = validation_error.value.args[0]
    assert exception_msg == "'1000' is not of type 'integer'"


def test_valid_json():
    """Test Valid JSON."""
    validator = VignetteValidator("tests/data/vignette_valid.json")
    validator.validate()
