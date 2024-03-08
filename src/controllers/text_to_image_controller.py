import logging
from threading import Thread
from PySide6.QtCore import QObject, Signal, Slot
import torch
from controllers.utils.text_to_image_state import TextToImageState
from models.text_to_image_repository import TextToImageRepository


class TextToImageController(QObject):
	state = Signal('QVariantMap') # type: ignore
	is_initialized = False
	repository: TextToImageRepository

	def __init__(self):
		super().__init__()
		self.repository = TextToImageRepository()

	@Slot(str)
	def generate(self, input_text: str):
		self.state.emit(TextToImageState.INITIALIZING())
		Thread(target=self.generate_image, args=(input_text,)).start()

	def generate_image(self, input_text: str):
		try:
			if not self.is_initialized:
				self.repository.initialize()
				self.is_initialized = True
			output_image_path = self.repository.generateImage(prompt=input_text, progress_callback=self.__progress_callback)
			self.state.emit(TextToImageState.SUCCESS(image_path=output_image_path))
		except Exception as exception:
			self.repository.cleanup()
			logging.fatal(exception)
			self.state.emit(TextToImageState.ERROR(exception))

	def __progress_callback(self, progress: float):
		self.state.emit(TextToImageState.GENERATING_IMAGE(progress))
