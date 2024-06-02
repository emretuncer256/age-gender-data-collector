from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QPushButton, QFileDialog, QApplication, QMainWindow, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from base64 import b64encode, b64decode

from logger import logger

from datetime import datetime
import shutil


class PDFViewer(QFrame):
    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)

        self.setLayout(QVBoxLayout(self))

        self.webView = QWebEngineView()
        self.webView.settings().setAttribute(
            self.webView.settings().WebAttribute.PluginsEnabled, True)
        self.webView.settings().setAttribute(
            self.webView.settings().WebAttribute.PdfViewerEnabled, True)
        self.layout().addWidget(self.webView)

        self.downloadButton = QPushButton("Download")
        self.downloadButton.clicked.connect(self.downloadPDF)

        self.layout().addWidget(self.downloadButton)

    def openPDF(self, path: str) -> None:
        filename = path.replace('\\', '/')
        self.webView.setUrl(QUrl("file:///" + filename))
        logger.info(f"PDF file opened from: {filename}")

    def openBytePDF(self, bytePdf: bytearray) -> None:
        base64Pdf = b64encode(bytePdf).decode("utf-8")
        self.webView.setUrl(QUrl(f"data:application/pdf;base64,{base64Pdf}"))
        logger.info(f"PDF file loaded as b64")

    def downloadPDF(self) -> None:
        url = self.webView.url().toString()
        if not url:
            return

        dt = datetime.now().date()
        targetPath, _ = QFileDialog.getSaveFileName(
            self, "Save File", f"report-{str(dt)}.pdf", "PDF Files (*.pdf)")
        if not targetPath:
            return

        if url.startswith("file:///"):
            sourcePDF = url[8:]
            shutil.copy(sourcePDF, targetPath)
            logger.info(f"PDF file copied {sourcePDF} to target {targetPath}")
        else:
            data = url.split(",")[1]
            data = b64decode(data)
            with open(targetPath, "wb") as file:
                file.write(data)
                logger.info(
                    f"PDF file decoded and copied to target {targetPath}")
        QMessageBox.information(
            self, "PDF Saved", f"PDF file saved to:\n{targetPath}")
