import platform
from typing import Optional
from invoke.tasks import task
from invoke.context import Context
from pathlib import Path
import shutil
import os
from tasks_utils import get_python_command, cleanup_compressed_files

app_name = "ImageDreamer"
app_version = "1.0"

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

###### Building the executable ######

@task(help={
	'show_terminal': 'Show terminal window (True by default, although it might be safe to use False)',
})
def build(ctx: Context, show_terminal: bool = True):
	'''
	Build the application using PyInstaller, please remove build, dist and ImageDreamer.spec files if got any error.
	After running the command successfully, run the executable with `invoke run-executable`.
	Run with --no-show-terminal to create a macOS ".app", see "create-appimage" command for Linux AppImages

	Args:
		ctx (Context): The invoke context.
	'''
	try:
		# files cleanup
		shutil.rmtree('build', onerror=lambda _, __, ___: None)
		shutil.rmtree('dist', onerror=lambda _, __, ___: None)
		try:
			os.remove(f'{app_name}.spec')
		except FileNotFoundError:
			pass
		# run pyinstaller command
		windowed_or_not = '' if show_terminal else '--windowed '
		command = f'pyinstaller --name {app_name} --clean --noconfirm {windowed_or_not}--hidden-import=pathlib --exclude-module triton --exclude-module datasets --exclude-module pandas --exclude-module gmpy2 --icon=resources/app_icon.ico --add-data "src/views:views" --add-data "src/assets:assets" src/main.py'
		ctx.run(command)
	except Exception as e:
		print(f'An error occurred while building the executable: {e}')
		print('Make sure you have "pyinstaller" installed by running "conda install pyinstaller" or "pip install pyinstaller"')
		print(f'If you have recursion limits, simply add "import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)" at the beggining of the "{app_name}.spec" file, then run "pyinstaller {app_name}.spec"')

@task
def create_tar_ball(ctx: Context):
	'''
	Compress program and its folders.
	'''
	output_file_path = f'dist/{app_name}/image_dreamer_no_model.tar.gz'
	cleanup_compressed_files()
	ctx.run(f'tar -czvf "{output_file_path}" dist/{app_name}/')

@task
def create_7zip(ctx: Context):
	'''
	Compress program and its folders. You need p7zip-full.
	'''
	output_file_path = f'dist/{app_name}/image_dreamer_no_model.7z'
	cleanup_compressed_files()
	ctx.run(f'7z a -t7z -m0=lzma2 -mx=9 -ms=on {output_file_path} dist/{app_name}/')

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
		execute_command = str(Path(f'./dist/{app_name}/{app_name}.exe'))
	else:
		execute_command = str(Path(f'./dist/{app_name}/{app_name}'))

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

# Generate AppImage for linux

@task
def create_appimage(ctx):
	appdir_path = Path(f'{app_name}-{app_version}.AppDir')
	dist_path = Path('dist')

	# Step 1: Prepare the AppDir structure
	if appdir_path.exists():
		shutil.rmtree(appdir_path)
	appdir_path.mkdir(parents=True, exist_ok=True)
	(appdir_path / 'usr/bin').mkdir(parents=True, exist_ok=True)
	(appdir_path / 'usr/lib').mkdir(parents=True, exist_ok=True)
	(appdir_path / 'usr/share/applications').mkdir(parents=True, exist_ok=True)
	(appdir_path / 'usr/share/icons/hicolor/scalable/apps').mkdir(parents=True, exist_ok=True)

	# Step 2: Copy files to AppDir
	# Assuming the executable and all dependencies are in the 'dist' directory
	for item in (dist_path / app_name).iterdir():
		if item.is_dir():
			shutil.copytree(item, appdir_path / 'usr/bin' / item.name, dirs_exist_ok=True)
		else:
			shutil.copy(item, appdir_path / 'usr/bin')

	# Copying the desktop and icon files
	shutil.copy(f'resources/{app_name}.desktop', appdir_path / 'usr/share/applications')
	shutil.copy(f'resources/{app_name}.desktop', appdir_path)
	shutil.copy('src/assets/app_icon.png', appdir_path / f'{app_name}.png')
	shutil.copy('src/assets/app_icon.png', appdir_path / f'usr/share/icons/hicolor/scalable/apps/{app_name}.png')

	# Making a symbolic link for the AppRun (this is required by AppImage)
	(appdir_path / 'AppRun').symlink_to(Path('usr/bin') / app_name)

	# Step 3: Use appimagetool to generate the AppImage
	# download your appropiate file from: https://github.com/AppImage/AppImageKit/releases
	cmd = f'resources/appimagetool-x86_64.AppImage {appdir_path}'
	ctx.run(cmd, echo=True)

	# remove appdir folder
	shutil.rmtree(appdir_path)

	# create AppImage file
	package_command = f'resources/appimagetool-x86_64.AppImage {appdir_path}'
	ctx.run(package_command)

	make_it_executable = f'chmod +x {app_name}-x86_64.AppImage'
	ctx.run(make_it_executable)

	print(f'AppImage for {app_name} has been created.')
