import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ApplicationWindow {
	id: window
	visible: true
	width: 480
	height: 640
	minimumWidth: 480
	minimumHeight: 640
	title: "Image Dreamer"

	ColumnLayout {
		spacing: 10
		anchors.fill: parent

		ScrollView {
			Layout.fillWidth: true
			Layout.preferredHeight: 80
			TextArea {
				id: inputText
				wrapMode: TextEdit.Wrap
				placeholderText: "Describe an image..."
				font.pointSize: 12

				Keys.onPressed: function (event) {
					if (event.key === Qt.Key_Enter || event.key === Qt.Key_Return) {
						event.accepted = true // Prevents the default behavior (new line)
						textToImageController.generate(inputText.text)
					}
				}

				TapHandler {
					acceptedButtons: Qt.RightButton
					onTapped: (qEventPoint) => {
						inputTextContextMenu.x = qEventPoint.scenePosition.x
						inputTextContextMenu.y = qEventPoint.scenePosition.y
						inputTextContextMenu.visible = true
					}
				}
			}
		}

		Menu {
			id: inputTextContextMenu
			MenuItem {
				text: "Cut"
				onTriggered: inputText.cut()
			}
			MenuItem {
				text: "Copy"
				onTriggered: inputText.copy()
			}
			MenuItem {
				text: "Paste"
				onTriggered: inputText.paste()
			}
			MenuItem {
				text: "Select All"
				onTriggered: inputText.selectAll()
			}
		}

		Button {
			Layout.alignment: Qt.AlignHCenter
			Layout.minimumWidth: 150
			Layout.minimumHeight: 35
			id: generateImageButton
			text: "Generate"
			font.pointSize: 12
			onClicked: textToImageController.generate(inputText.text)
		}

		Rectangle {
			color: "#DDDDDD"
			Layout.preferredWidth: 390
			Layout.preferredHeight: 390
			Layout.fillWidth: true
			Layout.fillHeight: true
			id: placeholderImageRectangle
			ColumnLayout {
				anchors.centerIn: parent
				Image {
					Layout.fillWidth: true
					width: 128
					height: 128
					source: "../assets/image_placeholder.svg"
					fillMode: Image.Pad
					sourceSize.width: 128
					sourceSize.height: 128
					visible: true
					smooth: true
				}
				Text {
					Layout.fillWidth: true
					text: "Developed by **Daniel Illescas Romero**"
					font.pointSize: 10
					textFormat: Text.MarkdownText
				}
				Text {
					Layout.fillWidth: true
					text: "Code available at [GitHub](https://github.com/illescasDaniel/ImageDreamer-QT-QUICK-MVC)"
					font.pointSize: 10
					textFormat: Text.MarkdownText
					onLinkActivated: (link) => Qt.openUrlExternally(link)
				}
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
			ToolTip.visible: hoverHandler.hovered
			ToolTip.text: "Left click to open image. Right click for additional options."
			ToolTip.delay: 300
			ToolTip.timeout: 6000
			HoverHandler {
				id: hoverHandler
				acceptedDevices: PointerDevice.AllDevices
				cursorShape: Qt.PointingHandCursor
			}
			TapHandler {
				acceptedButtons: Qt.LeftButton
				onTapped: (qEventPoint) => {
					const imagePath = outputImageView.source
					if (imagePath) {
						Qt.openUrlExternally(imagePath)
					}
				}
			}
			TapHandler {
				acceptedButtons: Qt.RightButton
				onTapped: (qEventPoint) => {
					imageContextMenu.x = qEventPoint.scenePosition.x
					imageContextMenu.y = qEventPoint.scenePosition.y
					imageContextMenu.visible = true
				}
			}
		}
	}

	Menu {
		id: imageContextMenu
		MenuItem {
			text: "Copy"
			onTriggered: {
				const imagePath = outputImageView.source
				if (imagePath) {
					textToImageController.copy_image_to_clipboard(imagePath)
				}
			}
		}
		MenuItem {
			text: "Open Pictures folder"
			onTriggered: Qt.openUrlExternally(textToImageController.pictures_path())
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
		id: progressViewPopup
		source: "ProgressViewPopup.qml"
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
				progressViewPopup.item.visible = true
				progressViewPopup.item.progressValue = 0
				progressViewPopup.item.progressIsIndeterminate = true
				const downloadedDataInMegabytes = state.downloadedDataInMegabytes
				if (downloadedDataInMegabytes && downloadedDataInMegabytes > 10) {
					const formattedValue = Math.floor(downloadedDataInMegabytes)
					progressViewPopup.item.title = `Loading components\n${formattedValue}MB / +7GB`
				} else {
					progressViewPopup.item.title = "Loading components"
				}
				outputImageView.source = ""
				outputImageView.visible = false
				placeholderImageRectangle.visible = true
				errorMessageDialog.detailedText = ""
				break
			case textToImageState.generatingImage:
				const percentageProgress = Math.floor(state.progress * 100)
				progressViewPopup.item.title = `Generating image: ${percentageProgress < 10 ? '  ' : percentageProgress < 100 ? ' ' : ''}${percentageProgress}%`
				progressViewPopup.item.progressIsIndeterminate = false
				progressViewPopup.item.progressValue = state.progress
				if (state.progress > 0 && state.imagePath) {
					outputImageView.source = state.imagePath
					placeholderImageRectangle.visible = false
					outputImageView.visible = true
				}
				break
			case textToImageState.success:
				progressViewPopup.item.visible = false
				generateImageButton.enabled = true
				outputImageView.source = state.imagePath
				placeholderImageRectangle.visible = false
				outputImageView.visible = true
				break
			case textToImageState.error:
				progressViewPopup.item.visible = false
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
