import subprocess
import os


def get_python_command() -> str:
	"""Determine the Python command based on the availability of 'python3' or 'python'."""
	try:
		# Try to run `python3 --version`
		subprocess.run(["python3", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
		return "python3"
	except (subprocess.CalledProcessError, FileNotFoundError):
		# Fallback to `python` if `python3` is not available
		return "python"

def cleanup_compressed_files():
	for file in ['dist/main/image_dreamer_no_model.7z', 'dist/main/image_dreamer_no_model.tar.gz']:
		try:
			os.remove(file)
		except FileNotFoundError:
			pass
