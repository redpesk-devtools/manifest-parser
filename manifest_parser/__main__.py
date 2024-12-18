"""Command-line tool to work with redpesk application manifests"""

import argparse
import logging
import sys
from enum import StrEnum

import colorlog

from .check import check
from .graph import graph


class SubCmd(StrEnum):
    """Enumeration of the available subcommands
    It is necessary to make an enumeration instead of just declaring these
    values as globals to avoid the SyntaxError "name capture makes remaining
    patterns unreachable" on the match statement.
    """

    CHECK_CMD = "check"
    EXPLAIN_CMD = "explain"
    GRAPH_CMD = "graph"


def setup_parser() -> argparse.ArgumentParser:
    """Creates and configures an ArgumentParser.
    Returns: the argparse.ArgumentParser object
    """
    parser = argparse.ArgumentParser(
        description="tooling to work with redpesk application manifests",
        epilog="source: https://github.com/redpesk-devtools/manifest-parser",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-l",
        "--log",
        default="info",
        help="threshold level for logging",
        choices=["debug", "info", "warning", "error", "critical"],
    )
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    # check parser
    check_parser = subparsers.add_parser(
        SubCmd.CHECK_CMD, help="verify and lint a manifest file"
    )
    check_parser.add_argument(
        "paths", help="paths of the manifest files to check", nargs="*"
    )

    # explain parser
    explain_parser = subparsers.add_parser(
        SubCmd.EXPLAIN_CMD,
        help="generate a Markdown-formatted explanation of what a manifest file declares",
    )

    # graph parser
    graph_parser = subparsers.add_parser(
        SubCmd.GRAPH_CMD,
        help="generate a PlantUML graph showing how multiple manifests interact with each other",
    )
    graph_parser.add_argument(
        "-o",
        "--output",
        default="graph",
        help="output file name (extension will be appended)",
    )
    graph_parser.add_argument(
        "-k",
        "--keep-puml",
        action="store_true",
        help="do not delete the PlantUML diagram description file",
    )
    graph_parser.add_argument(
        "-w",
        "--overwrite",
        action="store_true",
        help="overwrite output files which already exist",
    )
    graph_parser.add_argument(
        "-c", "--no-check", action="store_false", help="do not check if manifests are valid"
    )
    graph_parser.add_argument(
        "paths", help="paths of the manifest files to draw a graph for", nargs="+"
    )

    return parser


def setup_logging(log_level: str, log_to_stdout: bool = False) -> logging.Logger:
    """Creates and configure a colorful root logger.
    Args:
        log_level: log level under which logs are silenced
        log_to_stdout: True to log to stdout, False (default) to log to stderr
    Returns: the logging.Logger object
    """
    # setup colored logging
    handler = colorlog.StreamHandler()

    # logs of the check command should go to stdout, not stderr
    if log_to_stdout:
        handler.setStream(sys.stdout)

    handler.setFormatter(
        colorlog.ColoredFormatter(fmt="{log_color}{levelname:9}{reset}{message}", style="{")
    )
    logger = colorlog.getLogger()
    logger.setLevel(level=log_level)
    logger.addHandler(handler)

    return logger


def main():
    """manifest-parser CLI entrypoint"""
    parser = setup_parser()
    args = parser.parse_args()

    logger = setup_logging(args.log.upper(), args.subcommand == SubCmd.CHECK_CMD)

    # dispatch according to subcommand
    # subcommands are expected to terminate the program
    match args.subcommand:
        case None:
            parser.print_help()
            sys.exit(1)
        case SubCmd.CHECK_CMD:
            if check(args.paths, logger):
                logger.info("All manifests are valid")
                sys.exit(0)
            else:
                logger.warning(
                    "At least one manifest isn't valid, look for errors in above logs"
                )
                sys.exit(1)
        case SubCmd.GRAPH_CMD:
            graph(
                args.output,
                args.paths,
                args.keep_puml,
                args.overwrite,
                args.no_check,
                logger,
            )
        case SubCmd.EXPLAIN_CMD:
            raise NotImplementedError

if __name__ == "__main__":
    main()
