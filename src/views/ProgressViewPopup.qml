import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Popup {
	id: progressViewPopup
	visible: false
	modal: true
	focus: true
	padding: 8
	closePolicy: Popup.NoAutoClose
	x: (window.width - progressViewPopup.width) / 2
	y: (window.height - progressViewPopup.height) / 2
	property alias progressValue: progressBar.value
	property alias progressIsIndeterminate: progressBar.indeterminate
	property alias title: label.text

	ColumnLayout {
		anchors.centerIn: parent
		spacing: 10

		ProgressBar {
			Layout.alignment: Qt.AlignHCenter
			id: progressBar
			indeterminate: true
			value: 0
			ToolTip.visible: hovered && progressBar.indeterminate
			ToolTip.text: "Initial run may take a few minutes to download all components (around 7GB)."
			ToolTip.delay: 300
			ToolTip.timeout: 6000
		}

		Label {
			Layout.alignment: Qt.AlignHCenter
			id: label
			text: "Loading components"
			font.family: "monospace"
			horizontalAlignment: Text.AlignHCenter
			ToolTip.visible: ma.containsMouse && progressBar.indeterminate
			ToolTip.text: "Initial run may take a few minutes to download all components (around 7GB)."
			ToolTip.delay: 300
			ToolTip.timeout: 6000
			MouseArea {
				id: ma
				anchors.fill: parent
				hoverEnabled: true
			}
		}
	}
}
