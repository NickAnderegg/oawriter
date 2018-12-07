# -*- coding: utf-8 -*-

import argparse

from pathlib import Path

from oaspec import OASpecParser
from ..util import yaml

def generate_merged_specs(args):
    specs_dir = Path(args.specs_dir).resolve()

    try:
        amendments_dir = Path(args.amendments_dir).resolve(strict=True)
    except FileNotFoundError:
        print("No amendments directory found.")
        print("Run `oawriter template gen` to create amendment files before running this command.")
        exit()

    if "output_dir" not in args:
        if "merged_dir" in args:
            output_dir = args.merged_dir
        else:
            output_dir = "specs_merged"
    else:
        output_dir = args.output_dir
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(exist_ok=True)

    for spec_file in specs_dir.iterdir():
        if "-amendments" in spec_file.stem:
            continue

        try:
            amendments_file = (amendments_dir / spec_file.name).with_suffix(".yaml").resolve(strict=True)
        except FileNotFoundError:
            print(f"No amendments file found for {spec_file.name}. Skipping...")
            continue

        merged_file = output_dir / spec_file.stem
        merged_file_yaml = merged_file.with_suffix(".yaml").resolve()
        merged_file_json = merged_file.with_suffix(".json").resolve()

        parsed_spec = OASpecParser(str(spec_file)).parse_spec()

        with amendments_file.open("r", encoding="utf-8") as f:
            amendments_spec = yaml.load(f)

        parsed_spec._amend(amendments_spec)
        parsed_spec._dump_yaml(merged_file_yaml)
        parsed_spec._dump_json(merged_file_json)

def make_generate_parser(parent_parser, common_parser):

    generate_parser = parent_parser.add_parser(
        "generate",
        parents=[
            common_parser,
        ],
        help="Generate full specifications"
    )

    generate_parser.add_argument(
        "-o",
        "--output-dir",
        metavar="DIR",
        dest="output_dir",
        nargs=1,
        default="specs_merged",
        help="directory to output individual merged specs",
    )

    generate_parser.set_defaults(arg_processor=generate_merged_specs)
