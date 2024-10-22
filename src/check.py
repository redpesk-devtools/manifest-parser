"""Implementation of the check subcommand"""

import json
import logging

import jsonschema
import yaml


SCHEMA_FILENAME = "manifest.schema.json"


def check(path: str, logger: logging.Logger):
    """Reads a manifest file and checks its correctness according to the specification available
    here https://docs.redpesk.bzh/docs/en/master/developer-guides/manifest.yml.html
    Args:
        path: path to the manifest file to check
        logger: logger object
    """
    logger = logger.getChild(__name__)

    # load the manifest file from the path provided as argument
    try:
        with open(path, mode="r", encoding="utf-8") as manifest_file:
            manifest = yaml.safe_load(manifest_file)
    except OSError:
        logger.exception("%s could not be read", path)
        logger.critical("The file could not be read (check path and permission)")
        return False
    except yaml.parser.ParserError:
        logger.exception("%s does not look like a valid YAML file", path)
        logger.critical("The file could not be parsed")
        return False
    except yaml.scanner.ScannerError:
        logger.exception("%s does not look like a valid YAML file", path)
        logger.critical(
            "The file could not be parsed"
            " (check that you don't use @ or ` which are reserved YAML characters)"
        )
        logger.warning(
            "Know that this program only works on complete YAML files"
            " and will fail on template files (i.e. CMake's configure_file)"
        )
        return False
    logger.info("Manifest loaded from %s", path)

    # load the schema file from SCHEMA_FILENAME in the same directory as this source file
    schema_path = f"{'/'.join(__file__.split('/')[:-1])}/{SCHEMA_FILENAME}"
    with open(schema_path, mode="r", encoding="utf-8") as schema_file:
        schema = json.load(schema_file)
    logger.info("Schema loaded from %s", schema_path)

    # run the validation
    jsonschema.validate(manifest, schema)
