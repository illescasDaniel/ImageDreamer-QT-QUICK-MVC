from pathlib import Path
import sys
import logging
import argparse

from models.utils.stream_to_logger import StreamToLogger


class AppUtils:
	_app_base_path: Path

	@staticmethod
	def is_app_frozen() -> bool:
		# Define the base path depending on whether we're frozen (via PyInstaller)
		if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
			return True
		else:
			return False

	@staticmethod
	def app_base_path() -> Path:
		return AppUtils._app_base_path

	@staticmethod
	def set_app_base_path(base_path: Path):
		AppUtils._app_base_path = base_path

	@staticmethod
	def set_up_frozen_app_logging():
		logging.basicConfig(
			filename='app.log',  # Log file path
			filemode='a',  # Append mode ('w' for overwrite mode)
			format='%(asctime)s - %(levelname)s - %(message)s',  # Format of log messages
			datefmt='%Y-%m-%d %H:%M:%S',  # Format of timestamps
			level=logging.WARNING  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
		)
		sys.stdout = StreamToLogger(logging.getLogger('STDOUT'), logging.INFO)
		sys.stderr = StreamToLogger(logging.getLogger('STDERR'), logging.ERROR)
		from diffusers.utils.logging import disable_progress_bar
		disable_progress_bar()

	@staticmethod
	def set_up_logging(logging_level: int):
		default_log_level_str = AppUtils.__logging_to_string(logging_level)
		parser = argparse.ArgumentParser(description="Run the application with specified logging level.")
		parser.add_argument(
			"--log",
			default=default_log_level_str,
			choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
			help="Set the logging level (default: %(default)s)"
		)

		log = parser.parse_args().log or default_log_level_str

		logging.basicConfig(level=getattr(logging, log),
							format='%(asctime)s - %(levelname)s - %(message)s',
							datefmt='%Y-%m-%d %H:%M:%S')

	@staticmethod
	def __logging_to_string(logging_level: int) -> str:
		match logging_level:
			case logging.CRITICAL:
				return 'CRITICAL'
			case logging.ERROR:
				return 'ERROR'
			case logging.WARNING:
				return 'WARNING'
			case logging.INFO:
				return 'INFO'
			case logging.DEBUG:
				return 'DEBUG'
			case logging.NOTSET:
				return 'NOTSET'
			case _:
				return 'NOTSET'
