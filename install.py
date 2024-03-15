#!/usr/bin/env python3

import platform
import subprocess
import argparse


def setup_conda_environment(os_name: str, is_dev: bool):
	env_suffix = "_dev" if is_dev else ""
	env_file = f'./conda-environments/environment_{os_name}{env_suffix}.yaml'
	subprocess.call(['conda', 'env', 'create', '-f', env_file])

if __name__ == "__main__":
	try:
		parser = argparse.ArgumentParser(description='Project setup.')
		# action=store_true => if the command-line argument is specified, the relevant variable is set to True
		parser.add_argument('-d', '--dev', action='store_true', help='Set-up the development environment')
		# Parse the command-line arguments
		args = parser.parse_args()
		os_name = platform.system().lower()
		setup_conda_environment(os_name, is_dev=args.dev)
		print("Setup completed successfully.")
	except Exception as e:
		print(f"Error during setup: {e}")
