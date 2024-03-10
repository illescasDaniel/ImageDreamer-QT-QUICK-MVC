import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ApplicationWindow {
	id: window
	visible: true
	width: 390
	height: 540
	minimumWidth: 390
	minimumHeight: 540
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
				placeholderText: "Enter an image description..."

				Keys.onPressed: function (event) {
					if (event.key === Qt.Key_Enter || event.key === Qt.Key_Return) {
						event.accepted = true // Prevents the default behavior (new line)
						textToImageController.generate(inputText.text)
					}
				}
			}
		}

		Button {
			Layout.alignment: Qt.AlignHCenter
			id: generateImageButton
			text: "Generate"
			onClicked: textToImageController.generate(inputText.text)
		}

		Rectangle {
			color: "#DDDDDD"
			Layout.preferredWidth: 390
			Layout.preferredHeight: 390
			Layout.fillWidth: true
			Layout.fillHeight: true
			id: placeholderImageRectangle
			Image {
				anchors.centerIn: parent
				width: 128
				height: 128
				source: "../assets/image_placeholder.svg"
				fillMode: Image.Pad
				sourceSize.width: 128
				sourceSize.height: 128
				visible: true
				smooth: true
			}
		}

		Image {
			Layout.preferredWidth: 390
			Layout.preferredHeight: 390
			Layout.fillWidth: true
			Layout.fillHeight: true
			id: outputImageView
			source: ""
			fillMode: Image.PreserveAspectFit
			verticalAlignment: Image.AlignBottom
			smooth: true
			visible: false
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
				outputImageView.visible = false
				placeholderImageRectangle.visible = true
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
				placeholderImageRectangle.visible = false
				outputImageView.visible = true
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
