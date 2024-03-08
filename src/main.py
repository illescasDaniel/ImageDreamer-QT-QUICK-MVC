import platform
import sys
import logging
from pathlib import Path
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
import torch
from controllers.text_to_image_controller import TextToImageController
from models.utils.app_utils import AppUtils


if __name__ == "__main__":

	app = QGuiApplication(sys.argv)

	if platform.system() == 'Windows':
		QQuickStyle.setStyle("Universal")
	else:
		QQuickStyle.setStyle("Default")

	engine = QQmlApplicationEngine()

	textToImageController = TextToImageController()

	context = engine.rootContext()
	context.setContextProperty("textToImageController", textToImageController)

	if AppUtils.is_app_frozen():
		py_installer_path = sys._MEIPASS # type: ignore
		AppUtils.set_app_base_path(Path(py_installer_path))
		AppUtils.set_up_logging(logging.WARNING)
	else:
		app_path = Path(__file__).resolve().parent
		AppUtils.set_app_base_path(app_path)
		AppUtils.set_up_logging(logging.DEBUG)

	qml_file_path = AppUtils.app_base_path() / 'views' / 'main.qml'
	engine.load(qml_file_path)

	if not engine.rootObjects():
		sys.exit(-1)
	torch.cuda.empty_cache()
	sys.exit(app.exec())
