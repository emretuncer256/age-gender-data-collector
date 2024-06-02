from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from app_ui import Ui_MainWindow
from reporting import ReportWindow
from utils import FaceDetector
from logger import logger

from db import DB

import sys
import pandas as pd


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.db = DB()
        self.timer = QTimer(self)
        self.detectorThread = FaceDetector(self)

        self.currentData = None

        self.db.connect()

        self.initSlotSignal()
        self.loadCameras()
        self.loadData()

        self.detectorThread.start()

    def initSlotSignal(self):
        self.statusLabel = QLabel("Ready")
        self.statusbar.addWidget(self.statusLabel)

        self.timer.timeout.connect(self.saveData)

        self.detectorThread.changePixmap.connect(self.displayFrame)
        self.detectorThread.status.connect(self.cameraLabel.setText)
        self.detectorThread.status.connect(self.statusLabel.setText)
        self.detectorThread.result.connect(self.setCurrentData)

        self.camerasCombobox.currentIndexChanged.connect(self.changeCamera)

        self.toggleCameraButton.clicked.connect(self.toggleCamera)
        self.toggleDrawButton.clicked.connect(self.detectorThread.toggleDraw)

        self.startButton.clicked.connect(self.startButton_Clicked)

        self.deleteDBButton.clicked.connect(self.deleteDatabase)

        self.visualizeButton.clicked.connect(self.openVisualizationPanel)

        self.exportExcelButton.clicked.connect(self.exportAsExcel)
        self.exportSqlButton.clicked.connect(self.exportAsSql)
        self.exportCsvButton.clicked.connect(self.exportAsCsv)
        self.exportJsonButton.clicked.connect(self.exportAsJson)

        self.reloadButton.clicked.connect(self.loadData)
        self.clearButton.clicked.connect(self.clearTable)

        self.facesCheckbox.toggled.connect(
            lambda a0: self.detectorThread.setDrawOption("drawFace", a0)
        )
        self.ageCheckbox.toggled.connect(
            lambda a0: self.detectorThread.setDrawOption("drawAge", a0)
        )
        self.genderCheckbox.toggled.connect(
            lambda a0: self.detectorThread.setDrawOption("drawGender", a0)
        )

    def loadCameras(self):
        # TODO: Implement logic to list available cameras
        cameraList = [0, 1, 2]
        for cam in cameraList:
            self.camerasCombobox.addItem(f"CAM {cam}", cam)

    def displayFrame(self, frame: QImage):
        self.cameraLabel.setPixmap(QPixmap.fromImage(frame))

    def clearTable(self):
        self.table.setRowCount(0)

    def loadData(self):
        self.clearTable()
        result = self.db.fetchAll()
        for i, c, a, g, d in result:
            rowPos = self.table.rowCount()
            self.table.insertRow(rowPos)

            self.table.setItem(rowPos, 0, QTableWidgetItem(str(i)))
            self.table.setItem(rowPos, 1, QTableWidgetItem(str(a)))
            self.table.setItem(rowPos, 2, QTableWidgetItem(str(g)))
            self.table.setItem(rowPos, 3, QTableWidgetItem(str(d)))
            self.table.setItem(rowPos, 4, QTableWidgetItem(str(c)))
        logger.info("Data loaded successfully")

    def setCurrentData(self, data: list):
        self.currentData = data

    def toggleCamera(self):
        self.stopGathering()
        if self.detectorThread.isRunning():
            self.detectorThread.terminate()
            self.detectorThread.setDetect(False)
            self.cameraLabel.clear()
            self.cameraLabel.setText("Camera closed")
            self.startButton.setDisabled(True)
        else:
            self.detectorThread.setDetect(True)
            self.detectorThread.start()
            self.startButton.setDisabled(False)

    def changeCamera(self, value: int):
        if self.detectorThread.isRunning():
            self.detectorThread.terminate()
        self.detectorThread.setCameraIndex(value)
        self.detectorThread.start()
        self.stopGathering()

    def startGathering(self):
        if self.timer.isActive():
            return
        time = self.timeSpinbox.value() * 1000
        self.timer.start(time)
        self.startButton.setText("Stop")
        self.gatherStatusLabel.setText("Started")
        self.gatherStatusLabel.setStyleSheet("background: #5cb85c;")
        logger.info("Gathering started")

    def stopGathering(self):
        if not self.timer.isActive():
            return
        self.timer.stop()
        self.startButton.setText("Start")
        self.gatherStatusLabel.setText("Stopped")
        self.gatherStatusLabel.setStyleSheet("background: #f0ad4e;")
        self.currentData = None
        logger.info("Gathering stopped")

    def startButton_Clicked(self):
        if not self.timer.isActive():
            self.startGathering()
        else:
            self.stopGathering()

    def saveData(self):
        if not self.currentData:
            return

        for data in self.currentData:
            self.db.insertData(data)

        self.currentData = None
        self.loadData()

    def deleteDatabase(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Delete Database")
        dlg.setText("Do you want to delete database?")
        dlg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        dlg.setIcon(QMessageBox.Icon.Warning)
        button = dlg.exec()
        if button == QMessageBox.StandardButton.Yes:
            self.db.clearDatabase()
            logger.info("Database deleted")
            self.loadData()

    def dataToDataFrame(self):
        columns = [
            "ID",
            "Cam",
            "Age",
            "Gender",
            "Datetime"
        ]
        data = self.db.fetchAll()
        return pd.DataFrame(data, columns=columns)

    def exportAsExcel(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, 'Save Data', 'data.xlsx', 'Excel Files (*.xlsx)')
        if not filepath:
            return
        data = self.dataToDataFrame()
        data.to_excel(filepath, "Data")

        self.statusbar.showMessage("Excel file exported successfully", 3000)
        QMessageBox.information(self, "Data exported",
                                "The data exported as excel successfully.")

    def exportAsSql(self):
        # TODO: SQLAlchemy can be used to export.
        filepath, _ = QFileDialog.getSaveFileName(
            self, 'Save Data', 'data.sql', 'SQL Files (*.sql)')
        if not filepath:
            return
        data = self.dataToDataFrame()
        data.to_sql(filepath, self.db.conn)

        self.statusbar.showMessage("Sql file exported successfully", 3000)
        QMessageBox.information(self, "Data exported",
                                "The data exported as sql successfully.")

    def exportAsCsv(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, 'Save Data', 'data.csv', 'CSV Files (*.csv)')
        if not filepath:
            return
        data = self.dataToDataFrame()
        data.to_csv(filepath)

        self.statusbar.showMessage("CSV file exported successfully", 3000)
        QMessageBox.information(self, "Data exported",
                                "The data exported as csv successfully.")

    def exportAsJson(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, 'Save Data', 'data.json', 'JSON Files (*.json)')
        if not filepath:
            return
        data = self.dataToDataFrame()
        data.to_json(filepath)

        self.statusbar.showMessage("JSON file exported successfully", 3000)
        QMessageBox.information(self, "Data exported",
                                "The data exported as json successfully.")

    def showReportWindow(self):
        self.reportWindow = ReportWindow(self)
        self.reportWindow.showMaximized()
        logger.info("Report window created successfully")

    def openVisualizationPanel(self):
        if not hasattr(self, "reportWindow"):
            self.reportThread = QThread()
            self.reportThread.started.connect(self.showReportWindow)
            self.reportThread.start()
            logger.info("Report thread started successfully")
        elif not self.reportWindow.isVisible():
            if self.reportThread.isRunning():
                self.reportThread.terminate()
            self.reportWindow.close()

            del self.reportThread
            del self.reportWindow
            logger.info("Report window and thread destroyed")
            self.openVisualizationPanel()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
