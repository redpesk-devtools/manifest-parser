"""Command-line tool to work with redpesk application manifests"""

import argparse
import sys
from enum import StrEnum

import colorlog

from check import check
from graph import graph


class SubCmd(StrEnum):
    """Enumeration of the available subcommands
    It is necessary to make an enumeration instead of just declaring these
    values as globals to avoid the SyntaxError "name capture makes remaining
    patterns unreachable" on the match statement.
    """

    CHECK_CMD = "check"
    EXPLAIN_CMD = "explain"
    GRAPH_CMD = "graph"


# top-level CLI parser
parser = argparse.ArgumentParser(
    description="tooling to work with redpesk application manifests",
    epilog="source: https://github.com/redpesk-common/manifest-parser",
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

args = parser.parse_args()


# setup colored logging
handler = colorlog.StreamHandler()
# logs of the check command should go to stdout, not stderr
if args.subcommand == SubCmd.CHECK_CMD:
    handler.setStream(sys.stdout)
handler.setFormatter(
    colorlog.ColoredFormatter(fmt="{log_color}{levelname:9}{reset}{message}", style="{")
)
logger = colorlog.getLogger()
logger.setLevel(level=args.log.upper())
logger.addHandler(handler)


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
