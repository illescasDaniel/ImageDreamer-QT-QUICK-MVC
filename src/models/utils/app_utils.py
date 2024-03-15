import sys
import logging
import argparse
from pathlib import Path
from appdirs import user_data_dir
from urllib.parse import urlparse

from models.utils.stream_to_logger import StreamToLogger


class AppUtils:

	@staticmethod
	def is_app_frozen() -> bool:
		# Define the base path depending on whether we're frozen (via PyInstaller)
		if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
			return True
		else:
			return False

	@staticmethod
	def pictures_common_path() -> Path:
		pictures_dir = AppUtils.__writable_common_path() / 'Pictures'
		pictures_dir.mkdir(parents=True, exist_ok=True)
		return pictures_dir

	@staticmethod
	def uri_to_path(uri: str):
		parsed_uri = urlparse(uri)
		if parsed_uri.scheme == 'file':
			path = Path(parsed_uri.path)
			return str(path)
		else:
			raise ValueError("Invalid file URI")

	@staticmethod
	def set_up_frozen_app_logging():
		log_dir = AppUtils.__writable_common_path() / 'logs'
		log_dir.mkdir(parents=True, exist_ok=True)
		log_file = log_dir / 'app.log'
		logging.basicConfig(
			filename=log_file,
			filemode='a',  # Append mode ('w' for overwrite mode)
			format='%(asctime)s - %(levelname)s - %(message)s',
			datefmt='%Y-%m-%d %H:%M:%S',
			level=logging.WARNING
		)
		sys.stdout = StreamToLogger(logging.getLogger('STDOUT'), logging.INFO)
		sys.stderr = StreamToLogger(logging.getLogger('STDERR'), logging.ERROR)
		from diffusers.utils.logging import disable_progress_bar
		disable_progress_bar()

	@staticmethod
	def set_up_logging(logging_level: int):
		parser = argparse.ArgumentParser(description="Run the application with specified logging level.")
		parser.add_argument(
			"--log-level",
			default=logging.getLevelName(logging_level),
			choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
			help="Set the logging level (default: %(default)s)"
		)
		logging.basicConfig(level=logging.getLevelName(str(parser.parse_args().log_level)),
							format='%(asctime)s - %(levelname)s - %(message)s',
							datefmt='%Y-%m-%d %H:%M:%S')

	# Private

	@staticmethod
	def __writable_common_path() -> Path:
		appname = 'ImageDreamer'
		appauthor = 'Daniel Illescas Romero'
		common_path = Path(user_data_dir(appname, appauthor))
		common_path.mkdir(parents=True, exist_ok=True)
		return common_path