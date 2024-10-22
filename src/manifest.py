"""Command-line tool to work with redpesk application manifests"""

import argparse
import colorlog
from enum import StrEnum
import sys

from check import check


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
check_parser.add_argument("path", help="path of the manifest file to check")

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
args = parser.parse_args()


# setup colored logging
handler = colorlog.StreamHandler()
# logs of the check command should go to stdout, not stderr
if args.subcommand == SubCmd.CHECK_CMD:
    handler.setStream(sys.stdout)
handler.setFormatter(
    colorlog.ColoredFormatter(
        fmt="{log_color}{levelname:9}{name:8}{reset}{message}", style="{"
    )
)
logger = colorlog.getLogger()
logger.setLevel(level=args.log.upper())
logger.addHandler(handler)


# dispatch according to subcommand
match args.subcommand:
    case None:
        parser.print_help()
        sys.exit(1)
    case SubCmd.CHECK_CMD:
        if check(args.path, logger):
            logger.info("Manifest file %s is correct", args.path)
            sys.exit(0)
        else:
            logger.error("Manifest file %s contains error(s)", args.path)
            sys.exit(1)
    case SubCmd.EXPLAIN_CMD:
        raise NotImplementedError
    case SubCmd.GRAPH_CMD:
        raise NotImplementedError
