import platform
from pathlib import Path
from typing import Optional

from invoke.tasks import task
from invoke.context import Context

from .common import get_python_command, app_name


@task(help={'log_level': 'Set the logging level (default: DEBUG)',})
def run(ctx: Context, log_level: Optional[str] = None):
	execute_command = f'{get_python_command()} src/main.py'
	if log_level is not None:
		execute_command += f' --log-level {log_level}'
	ctx.run(execute_command)

@task(help={'log_level': 'Optional: specify the log level.',})
def run_executable(ctx: Context, log_level: Optional[str] = None):
	execute_command: str
	if platform.system() == 'Windows':
		execute_command = str(Path(f'./dist/{app_name}/{app_name}.exe'))
	else:
		execute_command = str(Path(f'./dist/{app_name}/{app_name}'))
	if log_level is not None:
		execute_command += f' --log {log_level}'
	ctx.run(execute_command)

@task
def run_app_image(ctx: Context):
	execute_command = f'./{app_name}-x86_64.AppImage'
	ctx.run(execute_command)