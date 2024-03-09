import platform
import sys
import logging
from pathlib import Path

from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
import torch

from models.utils.app_utils import AppUtils

if __name__ == "__main__":

	if AppUtils.is_app_frozen():
		py_installer_path = sys._MEIPASS # type: ignore
		AppUtils.set_app_base_path(Path(py_installer_path))
		AppUtils.set_up_frozen_app_logging()
	else:
		app_path = Path(__file__).resolve().parent
		AppUtils.set_app_base_path(app_path)
		AppUtils.set_up_logging(logging.DEBUG)

	app = QGuiApplication(sys.argv)
	app_icon_path = str(AppUtils.app_base_path() / 'assets' / 'app_icon.png')
	app.setWindowIcon(QIcon(app_icon_path))

	if platform.system() == 'Windows':
		QQuickStyle.setStyle("Universal")
	else:
		QQuickStyle.setStyle("Default")

	engine = QQmlApplicationEngine()

	from controllers.text_to_image_controller import TextToImageController
	textToImageController = TextToImageController()

	context = engine.rootContext()
	context.setContextProperty("textToImageController", textToImageController)

	qml_file_path = AppUtils.app_base_path() / 'views' / 'main.qml'
	engine.load(qml_file_path)

	if not engine.rootObjects():
		sys.exit(-1)
	torch.cuda.empty_cache()
	sys.exit(app.exec())
