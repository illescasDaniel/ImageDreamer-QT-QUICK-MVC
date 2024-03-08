import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Popup {
	id: loadingPopup
	visible: false
	modal: true
	focus: true
	padding: 8
	closePolicy: Popup.NoAutoClose
	x: (window.width - loadingPopup.width) / 2
	y: (window.height - loadingPopup.height) / 2
	property alias progressValue: progressBar.value
	property alias progressIsIndeterminate: progressBar.indeterminate

	ColumnLayout {
		anchors.centerIn: parent
		spacing: 10

		ProgressBar {
			Layout.alignment: Qt.AlignHCenter
			id: progressBar
			indeterminate: true
			value: 0
		}

		Label {
			Layout.alignment: Qt.AlignHCenter
			text: "Processing..."
		}
	}
}
