from typing import Callable
from pathlib import Path

class GlobalStore:
	app_base_path: Path
	exit_handlers: list[Callable[[], None]] = []
