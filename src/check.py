"""Implementation of the check subcommand"""

import logging
import re
import yaml


GLOBAL_MUST_HAVE = [
    "rp-manifest",
    "id",
    "version",
]
GLOBAL_MAY_HAVE = [
    "description",
    "author",
    "license",
    "file-properties",
    "required-permission",
    "provided-binding",
]


def _check_global(manifest: dict, logger: logging.Logger):
    """Checks the global part of a manifest
    Args:
        manifest: dictionary representing the manifest file
        logger: logger object
    Returns True if the checks find no error, False otherwise
    """
    rc = True

    # check mandatory
    if "rp-manifest" not in manifest.keys():
        logger.error("global field 'rp-manifest' is missing")
        rc = False
    elif manifest["rp-manifest"] != 1:
        logger.error("global field 'rp-manifest' should have a value of 1 (number)")
        rc = False

    if "id" not in manifest.keys():
        logger.error("global field 'id' is missing")
        rc = False
    elif not re.compile(r"^[a-zA-Z0-9_.\-]+$").match(manifest["id"]):
        logger.error(
            "global field 'id' does not match the regex %s", r"^[a-zA-Z0-9_.\-]+$"
        )
        rc = False

    if "version" not in manifest.keys():
        logger.error("global field 'version' is missing")
        rc = False
    elif not re.compile(r"^[a-zA-Z0-9_.\-]+$").match(manifest["version"]):
        logger.error(
            "global field 'version' does not match the regex %s", r"^[a-zA-Z0-9_.\-]+$"
        )
        rc = False
    elif not re.compile(r"[0-9]+\.[0-9]+\.[0-9]+").match(manifest["version"]):
        logger.warning(
            "global field 'version' does not match semantic versioning (regex %s)",
            r"[0-9]+\.[0-9]+\.[0-9]+",
        )

    return rc


def _check_targets(manifest: dict, logger: logging.Logger):
    return True


def check(path: str, logger: logging.Logger) -> bool:
    """Reads a manifest file and checks its correctness according to the specification available
    here https://docs.redpesk.bzh/docs/en/master/developer-guides/manifest.yml.html
    Args:
        path: path to the manifest file to check
        logger: logger object
    Returns True if the manifest has no error (only warnings or less), False otherwise
    """
    logger = logger.getChild(__name__)

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

    return _check_global(manifest, logger) and _check_targets(manifest, logger)
