#!/usr/bin/python3
import os
import sys
import argparse
from config import KeyscoreConfig
from session import KeyscoreSession
from pyvis.network import Network
from loguru import logger

_PROG_NAME = "openkeyscore"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=_PROG_NAME,
        description="A modular information gathering tool with support for many sources of OSINT."
    )
    parser.add_argument("ksdfile", help="Path to .ksd file containing the initial set of information nodes")
    parser.add_argument("-d", "--depth", help="Maximum depth of nodes to analyze before stopping (default: 5)", type=int, default=5)
    parser.add_argument("--html", help="Name of the HTML output file, if one should be created", type=str)
    parser.add_argument("-l", "--log-level", help="Minimum log level which should be output. (default: INFO)", type=str)
    parser.add_argument("--html-default-wait", help="Amount of seconds to wait, by default, when navigating to a website for screenscraping. (default: 1)", type=int, default=1)

    args = parser.parse_args()
    logger.remove()
    logger.add(sys.stderr, level=args.log_level if args.log_level else "INFO")
    KeyscoreConfig._load_config_from_args(args)

    try:
        ksdpath = args.ksdfile
        if not os.path.exists(ksdpath) or not os.path.isfile(ksdpath):
            parser.print_usage()
            print(f"{_PROG_NAME}: error: Cannot find file specified: {ksdpath}")
            sys.exit(1)
        session = KeyscoreSession.from_ksd(ksdpath)
    except Exception as e:
        print(f"{_PROG_NAME}: error: {e}")
        sys.exit(1)

    processed_nodes = session.process()
    print(f"\nFound {len(processed_nodes)} node{'s' if len(processed_nodes) > 1 else ''} total:")
    for node in processed_nodes:
        print(f"{node._type_display_name.rjust(25, ' ')}: {node}")

    if args.html:
        filename = args.html if args.html.endswith(".html") else f"{args.html}.html"
        net = Network(directed=True)
        idx = 0
        for node in processed_nodes:
            net.add_node(idx, label=f"{node._type_display_name}\n{node}") # TODO: Figure out how to add metadata to this
            if node.parent is not None:
                parent_idx = 0
                while not node.parent.equals(processed_nodes[parent_idx]):
                    parent_idx = parent_idx + 1
                net.add_edge(parent_idx, idx)
            idx = idx + 1
        net.show(filename, notebook=False)