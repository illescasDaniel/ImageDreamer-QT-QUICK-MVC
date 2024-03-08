from typing import Optional
from invoke.tasks import task
from invoke.context import Context
import os
import subprocess


# @task(help={
# 	'snapshot_id': 'Your hugging face model id, found at $HOME/.cache/huggingface/hub/models--facebook--bart-large-cnn/snapshots/<snapshot id here>'
# })
# def build(ctx: Context, snapshot_id: str):
# 	'''
# 	Build the application using PyInstaller.
# 	After running the command successfully, run the executable with `invoke run-executable`.

# 	Args:
# 		ctx (Context): The invoke context.
# 		snapshot_id (str): The ID of the hugging face model snapshot.

# 	Example:
# 		`invoke build --snapshot-id=37f520fa929c961707657b28798b30c003dd100b`
# 	'''
# 	try:
# 		home_path = os.environ.get('HOME')
# 		command = f'pyinstaller -y --add-data "src/views:views" --add-data "{home_path}/.cache/huggingface/hub/models--facebook--bart-large-cnn/snapshots/{snapshot_id}:model_directory" src/main.py'
# 		ctx.run(command)
# 	except Exception as e:
# 		print(f'An error occurred while building the executable: {e}')
# 		print('Make sure you have "pyinstaller" installed by running "conda install pyinstaller" or "pip install pyinstaller"')
# 		print('If you have recursion limits, simply add "import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)" at the beggining of the "main.spec" file, then run "pyinstaller main.spec"')

# @task
# def run_executable(ctx: Context):
# 	'''
# 	Run the executable, located at './dist/main/main'.
# 	'''
# 	ctx.run('./dist/main/main')

# @task
# def run_executable_debug_logging(ctx: Context):
# 	'''
# 	Run the executable, located at './dist/main/main', with DEBUG logging.
# 	'''
# 	ctx.run('./dist/main/main --log DEBUG')

@task
def generate_requirements(ctx: Context):
	'''
	Generate requirements.txt using `pipreqs`.
	'''
	try:
		ctx.run("pipreqs ./src --savepath ./requirements.txt --force")
		print("requirements.txt generated successfully.")
	except Exception as e:
		print(f'An error occurred while generating requirements.txt: {e}')
		print('Make sure you have pipreqs installed by running "conda install pireqs" or "pip install pipreqs"')

@task
def run(ctx: Context):
	'''
	Run the main.py app. Make sure you have the necessary dependencies installed.
	'''
	ctx.run(f'{get_python_command()} src/main.py')

# @task(help={
# 	'show_prints': 'Force pytest to show prints even if the test passes.',
# 	'logging_level': 'Optional: specific logging level. None by default.',
# 	'test_name': 'Optional: specific test method to run. All by default.',
# })
# def test(
# 	ctx: Context,
# 		show_prints: bool = True,
# 		logging_level: Optional[str] = None,
# 		test_name: Optional[str] = None
# 	):
# 	'''
# 	Run pytest to execute unit tests.
# 	If a test_name is provided, only that test will be run.
# 	'''
# 	project_root = './'
# 	source_code_root = './src'
# 	os.environ['PYTHONPATH'] = f'{os.environ.get("PYTHONPATH")}:{project_root}:{source_code_root}'

# 	pytest_command = 'pytest --color=yes'
# 	# -rP: shows prints even if test passes
# 	if show_prints:
# 		pytest_command += f' -rP'
# 	if logging_level is not None:
# 		pytest_command += f' --log-cli-level={logging_level}'
# 	# If a test name is provided, format the command to run that specific test
# 	if test_name is not None:
# 		pytest_command += f' -k {test_name}'

# 	ctx.run(pytest_command)


# @task
# def test_report(ctx: Context):
# 	'''
# 	Run pytest to execute unit tests with coverage.
# 	'''
# 	project_root = './'
# 	source_code_root = './src'
# 	os.environ['PYTHONPATH'] = f'{os.environ.get("PYTHONPATH")}:{project_root}:{source_code_root}'

# 	ctx.run('pytest --color=yes --cov=src/ --cov-report xml tests/')

def get_python_command():
	"""Determine the Python command based on the availability of 'python3' or 'python'."""
	try:
		# Try to run `python3 --version`
		subprocess.run(["python3", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
		return "python3"
	except (subprocess.CalledProcessError, FileNotFoundError):
		# Fallback to `python` if `python3` is not available
		return "python"