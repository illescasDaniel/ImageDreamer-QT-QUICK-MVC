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
	def INITIALIZING(cls, total_downloaded_megabytes: Optional[float] = None) -> dict[str, Any]:
		return cls.__to_dict(cls.__INITIALIZING, total_downloaded_megabytes=total_downloaded_megabytes)

	@classmethod
	def GENERATING_IMAGE(cls, progress: float, temporary_image_path: Optional[Path]) -> dict[str, Any]:
		image_path_str = str()
		if temporary_image_path is not None:
			image_path_str = temporary_image_path.as_uri()
		return cls.__to_dict(cls.__GENERATING_IMAGE, progress=progress, image_path=image_path_str)

	@classmethod
	def SUCCESS(cls, image_path: Path) -> dict[str, Any]:
		return cls.__to_dict(cls.__SUCCESS, image_path=image_path.as_uri())

	@classmethod
	def ERROR(cls, exception: Exception) -> dict[str, Any]:
		return cls.__to_dict(cls.__ERROR, error_message_details=str(exception))

	@classmethod
	def __to_dict(
		cls,
		value: Enum,
		progress: Optional[float] = None,
		total_downloaded_megabytes: Optional[float] = None,
		image_path: Optional[str] = None,
		error_message_details: Optional[str] = None
	) -> dict[str, Any]:
		return {
			'value': value,
			'progress': progress,
			'totalDownloadedMegabytes': total_downloaded_megabytes,
			'imagePath': image_path,
			'error_message_details': error_message_details
		}