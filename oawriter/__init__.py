# -*- coding: utf-8 -*-

# Copyright (c) 2018 Platform.sh
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse

from .__version__ import *

from .generate import make_generate_parser
from .template import make_template_parser
from .merge import make_merge_parser

PROGRAMNAME="sqwasher"
VERSION=__version__
COPYRIGHT="(C) 2018 Platform.sh"

def main():

    parser = argparse.ArgumentParser(
        description="Manipulate OpenAPI Specification definitions"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        default=False,
        help="increase verbosity of output",
    )

    subparsers = parser.add_subparsers()

    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "-s",
        "--specs",
        metavar="DIR",
        dest="specs_dir",
        nargs=1,
        default="specs",
        help="directory containing specs to merge",
    )

    common_parser.add_argument(
        "--amendments-dir",
        metavar="DIR",
        dest="amendments_dir",
        default="specs_amendments",
        help="output directory for amendment files (default: specs_amendments)",
    )

    make_generate_parser(subparsers, common_parser)
    make_template_parser(subparsers, common_parser)
    make_merge_parser(subparsers, common_parser)
    # subparsers.add_parser("merge", parents=[merge_cli_parser])

    args = parser.parse_args()
    args.arg_processor(args)

    # print(parser.parse_args())
    # Generator(parser.parse_args())


if __name__ == "__main__":
    main()
