from enum import Enum, unique
from pathlib import Path
from typing import Any, Optional


@unique
class TextToImageState(Enum):
	__INITIALIZING = 2
	__GENERATING_IMAGE = 3
	__SUCCESS = 4
	__ERROR = 5

	@classmethod
	def INITIALIZING(cls) -> dict[str, Any]:
		return cls.__to_dict(cls.__INITIALIZING)

	@classmethod
	def GENERATING_IMAGE(cls, progress: float) -> dict[str, Any]:
		return cls.__to_dict(cls.__GENERATING_IMAGE,progress=progress)

	@classmethod
	def SUCCESS(cls, image_path: Path) -> dict[str, Any]:
		return cls.__to_dict(cls.__SUCCESS, image_path=str(image_path))

	@classmethod
	def ERROR(cls, exception: Exception) -> dict[str, Any]:
		return cls.__to_dict(cls.__ERROR, error_message_details=str(exception))

	@classmethod
	def __to_dict(
		cls,
		value: Enum,
		progress: Optional[float] = None,
		image_path: Optional[str] = None,
		error_message_details: Optional[str] = None
	) -> dict[str, Any]:
		return {
			'value': value,
			'progress': progress,
			'imagePath': image_path,
			'error_message_details': error_message_details
		}