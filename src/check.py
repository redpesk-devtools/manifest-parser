"""Implementation of the check subcommand"""

import json
import logging

import jsonschema

from common import load_manifest

SCHEMA_FILENAME = "manifest.schema.json"


def check_one(path: str, schema: dict, logger: logging.Logger) -> bool:
    """Reads a manifest file and checks its correctness according to the specification available
    here https://docs.redpesk.bzh/docs/en/master/developer-guides/manifest.yml.html
    Args:
        path: path to the manifest file to check
        schema: JSON Schema against which to verify the manifest
        logger: logger object
    Returns: true if the manifest is valid, false if it contains an error
    """
    # load the manifest file from the path provided as argument
    manifest = load_manifest(path, logger)
    if manifest is None:
        return False

    # run the validation
    try:
        jsonschema.validate(manifest, schema)
    except (jsonschema.exceptions.ValidationError, TypeError):
        logger.exception("Validation failed for %s", path)
        return False
    return True


def check(paths: list[str], logger: logging.Logger) -> bool:
    """Runs checks for a list of manifest files
    Args:
        paths: list of manifest file paths
        logger: logger object
    Returns: true if all manifests are valid, false if one or more manifests are broken
    """
    logger = logger.getChild(__name__)

    # load the schema file from SCHEMA_FILENAME in the same directory as this source file
    schema_path = f"{'/'.join(__file__.split('/')[:-1])}/{SCHEMA_FILENAME}"
    with open(schema_path, mode="r", encoding="utf-8") as schema_file:
        schema = json.load(schema_file)
    logger.info("Schema loaded from %s", schema_path)

    res = True
    for path in paths:
        res = check_one(path, schema, logger) and res
    return res
