"""Pieces of code used by multiple subcommands, and not belonging to one subcommand specifically"""

import logging
import yaml


def load_manifest(path: str, logger: logging.Logger) -> dict:
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
        logger.critical(
            "%s could not be read (check path and permission)", path, exc_info=True
        )
        return None
    except yaml.parser.ParserError:
        logger.critical("%s does not look like a valid YAML file", path, exc_info=True)
        return None
    except yaml.scanner.ScannerError:
        logger.critical(
            "%s does not look like a valid YAML file"
            " (check that you don't use @ or ` which are reserved YAML characters)",
            path,
            exc_info=True,
        )
        logger.warning(
            "Know that this program only works on complete YAML files"
            " and will fail on template files (i.e. CMake's configure_file)"
        )
        return None

    logger.debug("Loaded %s", path)
    return manifest
