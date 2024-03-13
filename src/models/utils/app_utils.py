import sys
import logging
import argparse

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
	def set_up_frozen_app_logging():
		logging.basicConfig(
			filename='app.log',
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
