"""Pieces of code used by multiple subcommands, and not belonging to one subcommand specifically"""

import logging
import yaml


def load_manifest(path: str, logger: logging.Logger) -> dict | None:
    """Load a manifest.yml from file.
    Args:
        path: path to the manifest file
        logger: logger object
    Returns: dictionary representing the parsed YAML data
    """
    try:
        with open(path, mode="r", encoding="utf-8") as manifest_file:
            manifest = yaml.safe_load(manifest_file)
    except OSError:
        logger.exception("%s could not be read", path)
        logger.critical("The file could not be read (check path and permission)")
        return None
    except yaml.parser.ParserError:
        logger.exception("%s does not look like a valid YAML file", path)
        logger.critical("The file could not be parsed")
        return None
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
        return None

    logger.info("Manifest loaded from %s", path)
    return manifest
