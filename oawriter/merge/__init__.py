# -*- coding: utf-8 -*-

import argparse

from pathlib import Path

from oaspec import OASpecParser
from ..util import yaml
from ..generate import generate_merged_specs

def generate_unified_spec(args):
    specs_dir = Path(args.specs_dir).resolve()

    generate_merged_specs(args)

    merged_dir = Path(args.merged_dir).resolve(strict=True)

    master_spec_file = Path(args.master_spec).resolve()
    if not master_spec_file.exists():
        print("No master file found.")
        print(f"Create a master file at {master_spec_file.name} to run this command")
        exit()

    field_template_file = Path(args.template_file).resolve()
    with field_template_file.open("r") as f:
        overwrites_config = yaml.load(f)["overwrites_config"]

    master_spec = OASpecParser(str(master_spec_file)).parse_spec(gentle_validation=True)

    for spec_file in merged_dir.iterdir():
        if spec_file.suffix != ".yaml":
            continue

        other_spec = OASpecParser(str(spec_file)).parse_spec()
        master_spec._update(other_spec, no_override=True, overwrites_config=overwrites_config)

    output_file = Path(args.output_name).resolve()
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file_yaml = output_file.with_suffix(".yaml").resolve()
    output_file_json = output_file.with_suffix(".json").resolve()

    master_spec._dump_yaml(output_file_yaml)
    master_spec._dump_json(output_file_json)

def make_merge_parser(parent_parser, common_parser):

    merge_parser = parent_parser.add_parser(
        "merge",
        parents=[
            common_parser,
        ],
        help="Generate unified specification"
    )

    merge_parser.add_argument(
        "-m",
        "--master",
        metavar="MASTER",
        dest="master_spec",
        default="master.yaml",
        help="master spec (default: master.yaml)",
    )

    merge_parser.add_argument(
        "-t",
        "--template",
        metavar="FILE",
        dest="template_file",
        default="field_config.yaml",
        help="location of field config file (default: field_config.yaml)"
    )

    merge_parser.add_argument(
        "-o",
        "--output",
        metavar="OUT",
        dest="output_name",
        default="swagger",
        help="output file for spec without suffix (default: swagger.{json, yaml})",
    )

    merge_parser.add_argument(
        "--merged-dir",
        metavar="DIR",
        dest="merged_dir",
        nargs=1,
        default="specs_merged",
        help="location where individual output specs will be stored",
    )

    merge_parser.set_defaults(arg_processor=generate_unified_spec)
