import platform
import sys
import logging
from pathlib import Path

from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from models.utils.app_utils import AppUtils
from models.utils.global_store import GlobalStore

def clean_up():
	for handler in GlobalStore.exit_handlers:
		handler()
	logging.debug('Closing app')

if __name__ == "__main__":

	if AppUtils.is_app_frozen():
		py_installer_path = sys._MEIPASS # type: ignore
		GlobalStore.app_base_path = Path(py_installer_path)
		AppUtils.set_up_frozen_app_logging()
	else:
		app_path = Path(__file__).resolve().parent
		GlobalStore.app_base_path = app_path
		AppUtils.set_up_logging(logging_level=logging.DEBUG)

	app = QGuiApplication(sys.argv)
	app_icon_path = str(GlobalStore.app_base_path / 'assets' / 'app_icon.png')
	app.setWindowIcon(QIcon(app_icon_path))
	app.aboutToQuit.connect(clean_up)

	if platform.system() == 'Windows':
		QQuickStyle.setStyle("Universal")
	else:
		QQuickStyle.setStyle("Default")

	engine = QQmlApplicationEngine()

	from controllers.text_to_image_controller import TextToImageController
	textToImageController = TextToImageController()

	context = engine.rootContext()
	context.setContextProperty("textToImageController", textToImageController)

	qml_file_path = GlobalStore.app_base_path / 'views' / 'main.qml'
	engine.load(qml_file_path)

	if not engine.rootObjects():
		sys.exit(-1)

	sys.exit(app.exec())
