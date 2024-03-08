import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ApplicationWindow {
	id: window
	visible: true
	width: 340
	height: 512
	minimumWidth: 340
	minimumHeight: 512
	title: "Image Dreamer"

	ColumnLayout {
		spacing: 10
		anchors.fill: parent

		ScrollView {
			Layout.fillWidth: true
			Layout.preferredHeight: 100
			TextArea {
				id: inputText
				wrapMode: TextEdit.Wrap
				placeholderText: "Enter text to summarize..."
			}
		}

		Button {
			Layout.alignment: Qt.AlignHCenter
			id: generateImageButton
			text: "Generate"
			onClicked: textToImageController.generate(inputText.text)
		}

		Image {
			Layout.preferredWidth: 340
			Layout.preferredHeight: 340
			Layout.fillWidth: true
			Layout.fillHeight: true
			id: outputImageView
			source: ""
			fillMode: Image.PreserveAspectFit
			verticalAlignment: Image.AlignBottom
			mipmap: true
		}
	}

	MessageDialog {
		id: errorMessageDialog
		text: "An error has ocurred"
		informativeText: "We are sorry, the image could not be generated."
		detailedText: ""
		buttons: MessageDialog.Ok
		visible: false
		onAccepted: {
			errorMessageDialog.visible = false
		}
	}

	Loader {
		id: popupLoader
		source: "LoadingPopup.qml"
		asynchronous: true
	}

	QtObject {
		id: textToImageState
		property var initializing: 2
		property var generatingImage: 3
		property var success: 4
		property var error: 5
	}

	Connections {
		target: textToImageController
		function onState(state) {
			switch (state.value) {
			case textToImageState.initializing:
				generateImageButton.enabled = false
				popupLoader.item.visible = true
				popupLoader.item.progressValue = 0
				popupLoader.item.progressIsIndeterminate = true
				outputImageView.source = ""
				errorMessageDialog.detailedText = ""
				break
			case textToImageState.generatingImage:
				popupLoader.item.progressIsIndeterminate = false
				popupLoader.item.progressValue = state.progress
				break
			case textToImageState.success:
				popupLoader.item.visible = false
				generateImageButton.enabled = true
				outputImageView.source = state.imagePath
				break
			case textToImageState.error:
				popupLoader.item.visible = false
				generateImageButton.enabled = true
				errorMessageDialog.detailedText = state.error_message_details
				errorMessageDialog.visible = true
				break
			default:
				break
			}
		}
	}
}
