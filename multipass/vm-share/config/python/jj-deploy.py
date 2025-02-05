#!/usr/bin/env -S PIPENV_IGNORE_VIRTUALENVS=1 pipenv-shebang
import argparse
import os

import yaml
from common.utils import run_cmd


def get_charm_path():
    current_directory = os.getcwd()
    # Find a file that ends in .charm
    for file in os.listdir(current_directory):
        if file.endswith(".charm"):
            return file


def get_resource_image_location():
    with open("charmcraft.yaml") as f:
        charmcraft_yaml = yaml.safe_load(f)
    resources = charmcraft_yaml.get("resources", {})
    return {resource: resources[resource]["upstream-source"] for resource in resources}


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", help="The name of the charm to deploy", type=str, default="")
    parser.add_argument("-n", help="The number of units to deploy", type=int, default=1)
    return parser.parse_args()


def main():
    args = get_args()
    charm_path = get_charm_path()
    resource_locations = get_resource_image_location()

    resource_args = [f"--resource {k}={v}" for k, v in resource_locations.items()]
    run_cmd(f"juju deploy ./{charm_path} {args.name} {' '.join(resource_args)} -n {args.n}")


if __name__ == "__main__":
    main()
