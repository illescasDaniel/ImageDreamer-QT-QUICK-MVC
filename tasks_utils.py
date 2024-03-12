import subprocess
import os
import platform
from pathlib import Path


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

def get_safetensors_path_or_exception(root_folder: str) -> Path:
	safetensors_file = next(Path(root_folder).glob('*.safetensors'), None)
	if safetensors_file is None:
		raise FileNotFoundError('File not found')
	return safetensors_file

def delete_unnused_files_for_built_program():
	files_safe_to_delete: list[str]
	match platform.system():
		case "Windows":
			files_safe_to_delete = __windows_safe_files_to_delete()
		case "Linux":
			files_safe_to_delete = __linux_safe_files_to_delete()
		case _:
			files_safe_to_delete = []
	for file in files_safe_to_delete:
		try:
			os.remove(file)
		except Exception as e:
			print(f'Error removing unnecessary file: {e}')
			
def __linux_safe_files_to_delete() -> list[str]:
	return [
		'dist/ImageDreamer/_internal/torch/lib/libcudnn_adv_train.so.8',
		'dist/ImageDreamer/_internal/torch/lib/libcudnn_ops_train.so.8',
		'dist/ImageDreamer/_internal/torch/lib/libcudnn_cnn_train.so.8',
		'dist/ImageDreamer/_internal/libcusolver.so.11',
	]

def __windows_safe_files_to_delete() -> list[str]:
	return [
		'dist/ImageDreamer/_internal/torch/lib/cudnn_adv_train64_8.dll',
		'dist/ImageDreamer/_internal/torch/lib/cudnn_cnn_train64_8.dll',
		'dist/ImageDreamer/_internal/torch/lib/cudnn_ops_train64_8.dll',
		'dist/ImageDreamer/_internal/cusolver64_11.dll',
	]