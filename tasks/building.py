import shutil
import os

from invoke.tasks import task
from invoke.context import Context

from .common import app_name


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
