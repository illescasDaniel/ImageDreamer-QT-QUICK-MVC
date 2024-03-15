import logging
from pathlib import Path
from threading import Thread
from typing import Optional

from PySide6.QtCore import QObject, Signal, Slot, QUrl
from PySide6.QtGui import QImage, QGuiApplication

from controllers.utils.text_to_image_state import TextToImageState
from models.text_to_image_repository import TextToImageRepository
from models.utils.app_utils import AppUtils
from models.utils.global_store import GlobalStore


class TextToImageController(QObject):
	state = Signal('QVariantMap') # type: ignore
	is_initialized = False
	repository: TextToImageRepository
	__image_generation_thread: Optional[Thread] = None

	def __init__(self):
		super().__init__()
		self.repository = TextToImageRepository()
		GlobalStore.exit_handlers.append(self.__wait_for_image_generation_to_finish)

	@Slot(str)
	def generate(self, input_text: str):
		self.__image_generation_thread = Thread(target=self.__generate_image, args=(input_text,))
		self.__image_generation_thread.start()

	@Slot(result=str)
	def pictures_path(self) -> str:
		return AppUtils.pictures_common_path().as_uri()

	@Slot(str)
	def copy_image_to_clipboard(self, imagePath):
		valid_path = AppUtils.uri_to_path(imagePath)
		app: QGuiApplication = QGuiApplication.instance() #type: ignore
		clipboard = app.clipboard()
		image = QImage(valid_path)
		if not image.isNull():
			clipboard.setImage(image)

	# Private

	def __generate_image(self, input_text: str):
		self.state.emit(TextToImageState.INITIALIZING())
		try:
			if not self.is_initialized:
				self.repository.initialize(self.__downloaded_data_callback)
				self.is_initialized = True
			output_image_path = self.repository.generateImage(
				prompt=input_text,
				progress_callback=self.__progress_callback
			)
			self.state.emit(TextToImageState.SUCCESS(image_path=output_image_path))
		except Exception as exception:
			self.repository.cleanup()
			logging.error(exception)
			self.state.emit(TextToImageState.ERROR(exception))

	def __downloaded_data_callback(self, data_in_megabytes: float):
		self.state.emit(TextToImageState.INITIALIZING(data_in_megabytes))

	def __progress_callback(self, progress: float, temporary_image_path: Optional[Path]):
		self.state.emit(TextToImageState.GENERATING_IMAGE(progress, temporary_image_path))

	def __wait_for_image_generation_to_finish(self):
		if self.__image_generation_thread is not None:
			self.__image_generation_thread.join(10)