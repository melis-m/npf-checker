import argparse
import os
import sys

global _args
global _parser


def parse_args():
    global _args
    global _parser

    _parser = argparse.ArgumentParser(
        description="A checker that ensure the validity and conformance of an NPF",
    )
    _parser.add_argument(
        'npf',
    )
    _parser.add_argument(
        '-c',
        '--cache-dir',
        default=os.path.join(
            os.getcwd(),
            os.path.dirname(sys.argv[0]),
            'cache',
        ),
        help="Cache directory used to unpack and check the NPF. Default: cache/",
    )
    _parser.add_argument(
        '--action',
        choices=['edit', 'fix', 'diff'],
        default='edit',
        help="Action to be used, 'edit' prompts the user the possible changes, 'fix' automatically applies all of them, and 'diff' only shows what would be automatically done"
    )
    _parser.add_argument(
        '--visual',
        action='store_true',
        help="Try to use more visual tools (only makes sense with --action=edit, which is the default)"
    )
    _parser.add_argument(
        '--config',
        default=os.path.join(
            os.getcwd(),
            os.path.dirname(sys.argv[0]),
            'Config.toml',
        ),
    )
    _args = _parser.parse_args()


def get_args():
    global _args
    return _args


def get_parser():
    global _parser
    return _parser
