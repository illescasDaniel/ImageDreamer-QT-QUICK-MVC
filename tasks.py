import platform
from typing import Optional
from invoke.tasks import task
from invoke.context import Context
from pathlib import Path
import shutil
import os
from tasks_utils import get_python_command, cleanup_compressed_files, get_safetensors_path_or_exception, delete_unnused_files_for_built_program

### Run app ##

@task(help={
	'log_level': 'Set the logging level (default: DEBUG)',
})
def run(ctx: Context, log_level: Optional[str] = None):
	'''
	Run the main.py app. Make sure you have the necessary dependencies installed.

	Args:
		log_level (Optional[str]): The log level, like DEBUG or WARNING.
	'''
	execute_command = f'{get_python_command()} src/main.py'
	if log_level is not None:
		execute_command += f' --log-level {log_level}'
	ctx.run(execute_command)

### Run tests ##

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

###### Building the executable ######

@task(help={
	'show_terminal': 'Show terminal window (True by default, although it might be safe to use False)',
})
def build(ctx: Context, show_terminal: bool = True):
	'''
	Build the application using PyInstaller, please remove build, dist and ImageDreamer.spec files if got any error.
	After running the command successfully, run the executable with `invoke run-executable`.

	Args:
		ctx (Context): The invoke context.
	'''
	try:
		# files cleanup
		shutil.rmtree('build', onerror=lambda _, __, ___: None)
		shutil.rmtree('dist', onerror=lambda _, __, ___: None)
		try:
			os.remove('ImageDreamer.spec')
		except FileNotFoundError:
			pass
		# run pyinstaller command
		windowed_or_not = '' if show_terminal else '--windowed '
		command = f'pyinstaller --name ImageDreamer -y {windowed_or_not}--hidden-import=pathlib --exclude-module triton --exclude-module datasets --exclude-module pandas --exclude-module gmpy2 --icon=resources/app_icon.ico --add-data "src/views:views" --add-data "src/assets:assets" src/main.py'
		ctx.run(command)
		# create an output folder for images generation
		os.makedirs('dist/ImageDreamer/output', exist_ok=True)
		# if we can delete certain files that we don't use, do so
		delete_unnused_files_for_built_program()
	except Exception as e:
		print(f'An error occurred while building the executable: {e}')
		print('Make sure you have "pyinstaller" installed by running "conda install pyinstaller" or "pip install pyinstaller"')
		print('If you have recursion limits, simply add "import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)" at the beggining of the "ImageDreamer.spec" file, then run "pyinstaller ImageDreamer.spec"')

@task
def create_tar_ball(ctx: Context):
	'''
	Compress program and its folders.
	'''
	output_file_path = 'dist/ImageDreamer/image_dreamer_no_model.tar.gz'
	cleanup_compressed_files()
	safetensors_file_path = str(get_safetensors_path_or_exception('dist/ImageDreamer/resources/models'))
	ctx.run(f'tar -czvf "{output_file_path}" --exclude="{safetensors_file_path}" dist/ImageDreamer/')

@task
def create_7zip(ctx: Context):
	'''
	Compress program and its folders. You need p7zip-full.
	'''
	output_file_path = 'dist/ImageDreamer/image_dreamer_no_model.7z'
	cleanup_compressed_files()
	safetensors_file_path = str(get_safetensors_path_or_exception('dist/ImageDreamer/resources/models'))
	ctx.run(f'7z a -t7z -m0=lzma2 -mx=9 -ms=on -x!{safetensors_file_path} {output_file_path} dist/ImageDreamer/')

@task(help={
	'log_level': 'Optional: specify the log level.',
})
def run_executable(ctx: Context, log_level: Optional[str] = None):
	'''
	Run the executable, located at './dist/ImageDreamer/ImageDreamer'.

	Args:
		log_level (Optional[str]): The log level, like DEBUG or WARNING.
	'''
	execute_command: str
	if platform.system() == 'Windows':
		execute_command = str(Path('./dist/ImageDreamer/ImageDreamer.exe'))
	else:
		execute_command = str(Path('./dist/ImageDreamer/ImageDreamer'))

	if log_level is not None:
		execute_command += f' --log {log_level}'

	ctx.run(execute_command)

# Other

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
