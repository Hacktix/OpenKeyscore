#!/usr/bin/python3
import os
import sys
import argparse
from config import KeyscoreConfig
from session import KeyscoreSession

_PROG_NAME = "openkeyscore"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=_PROG_NAME,
        description="A modular information gathering tool with support for many sources of OSINT."
    )
    parser.add_argument("ksdfile", help="Path to .ksd file containing the initial set of information nodes")
    parser.add_argument("-d", "--depth", help="Maximum depth of nodes to analyze before stopping", type=int, default=5)

    args = parser.parse_args()
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
    print(f"\nFound {len(processed_nodes)} nodes total:")
    for node in processed_nodes:
        print(f"\n  {node.__class__.__name__}:\n    {node}")