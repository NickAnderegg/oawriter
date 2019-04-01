# -*- coding: utf-8 -*-

import argparse

from pathlib import Path
from datetime import datetime
from copy import deepcopy
import shutil

from oaspec import OASpecParser
from ..util import yaml

_data_dir = Path(__file__).parent / "data"

def create_new_template(args):
    template_file = _data_dir / "_field_config.yaml"
    output_file = Path(args.template_file).resolve()

    if output_file.exists() and not args.force_overwrite:
        print(
            f"A field config file already exists at {output_file}.",
            f"To overwrite this file, call this command again with",
            f"the --force-overwrite flag.",
            sep=" ",
        )
        return

    shutil.copyfile(
        str(template_file),
        str(output_file),
    )

def parse_keys(field_template, spec):

    if isinstance(field_template, str):


        if field_template in spec:
            value_dict = {
                "__original": spec[field_template]._raw(),
                "__override": "",
            }


            if spec[field_template]._is_array():
                value_dict["__override"] = [""]

            return { field_template: value_dict }

        return {
            field_template: {
                "__override": "",
            }
        }
    elif isinstance(field_template, dict):
        parsed = dict()
        if "__keys__" in field_template:
            for key in field_template["__keys__"]:
                if key not in spec:
                    continue

                parsed_value = parse_keys(field_template["__include__"], spec[key])

                if parsed_value:
                    parsed[key] = parsed_value
        else:
            for key, val in field_template.items():
                if key in spec:
                    parsed_value = parse_keys(val, spec[key])

                    if parsed_value:
                        parsed[key] = parsed_value

                elif key == "*":
                    for prop in spec:
                        parsed_value = parse_keys(val, spec[prop])

                        if parsed_value:
                            parsed[prop] = parsed_value

        return parsed

    elif isinstance(field_template, list):
        if not spec._is_array():
            parsed = dict()
            for item in field_template:
                parsed.update(parse_keys(item, spec))
            return parsed
        else:
            parsed_items = list()
            for sub_item in spec:
                parsed = dict()
                for key in field_template:
                    parsed.update(parse_keys(key, sub_item))

                all_items = {k:str(sub_item[k]) for k in sub_item if k not in parsed}
                all_items.update(parsed)

                parsed_items.append(all_items)

            return parsed_items


def get_prev_amendments(curr, prev):
    merged = {}

    for key, curr_value in curr.items():
        if key not in prev:
            merged[key] = deepcopy(curr_value)
            continue

        # if isinstance(curr_value, list):
        #     merged[key] = list()
        #     for item in curr_value:
        #         merged[key].append(get_prev_amendments(item))
        if not isinstance(curr_value, dict):
            merged[key] = deepcopy(prev[key])
            continue

        merged[key] = {}
        if "__override" in curr_value:
            original_value = curr_value.get("__original", None)
            if original_value:
                merged[key]["__original"] = deepcopy(original_value)

            merged[key]["__override"] = deepcopy(prev[key].get("__override", ""))

        else:
            merged[key].update(
                get_prev_amendments(curr_value, prev[key])
            )

    return merged


def generate_from_template(args):
    specs_dir = Path(args.specs_dir).resolve()

    amendments_dir = Path(args.amendments_dir).resolve()
    amendments_dir.mkdir(exist_ok=True)

    field_template_file = Path(args.template_file).resolve()
    with field_template_file.open("r") as f:
        field_template = yaml.load(f)["fields"]

    for spec_file in specs_dir.iterdir():
        if "-amendments" in spec_file.stem:
            continue

        if specs_dir == amendments_dir:
            amendments_file_name = f"{spec_file.stem}-amendments.yaml"
        else:
            amendments_file_name = f"{spec_file.stem}.yaml"
        amendments_file = amendments_dir / amendments_file_name

        prev_amends_dir = amendments_dir / "prev_versions"
        prev_amends_dir.mkdir(exist_ok=True)

        if amendments_file.exists():
            curr_timestamp = datetime.utcnow()
            backup_file_name = "{}.{}{}{}".format(
                amendments_file.stem,
                curr_timestamp.strftime("%Y%m%d%H%M%S"),
                curr_timestamp.strftime("%f")[:2],
                amendments_file.suffix,
            )
            backup_file = prev_amends_dir / backup_file_name

            shutil.copyfile(
                str(amendments_file),
                str(backup_file),
            )

        parsed_spec = OASpecParser(str(spec_file)).parse_spec()
        parsed_template = parse_keys(field_template, parsed_spec)

        if amendments_file.exists() and not args.clean_template:
            with amendments_file.open("r", encoding="utf-8") as f:
                previous_amendments = yaml.load(f)

            parsed_template = get_prev_amendments(parsed_template, previous_amendments)

        with amendments_file.open("w", encoding="utf-8") as f:
            yaml.dump(parsed_template, f)

def make_template_parser(parent_parser, common_parser):

    template_common_parser = argparse.ArgumentParser(add_help=False)
    template_common_parser.add_argument(
        "-t",
        "--template",
        metavar="FILE",
        dest="template_file",
        default="field_config.yaml",
        help="location of field config file (default: field_config.yaml)"
    )

    template_parser = parent_parser.add_parser(
        'template',
        help="Generate and manage writing templates",
    )

    subparsers = template_parser.add_subparsers()

    template_new_parser = subparsers.add_parser(
        "new",
        parents=[
            template_common_parser
        ],
        help="Create a blank template configuration",
    )

    template_new_parser.add_argument(
        "-f",
        "--force-overwrite",
        action="store_true",
        dest="force_overwrite",
        help="overwrite an existing field template config",
    )

    template_new_parser.set_defaults(arg_processor=create_new_template)

    template_gen_parser = subparsers.add_parser(
        "gen",
        parents=[
            common_parser,
            template_common_parser
        ],
        help="Generate a writing template from a specification"
    )

    template_gen_parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        dest="clean_template",
        help="generate template without incorporating existing overrides",
    )

    template_gen_parser.set_defaults(arg_processor=generate_from_template)
