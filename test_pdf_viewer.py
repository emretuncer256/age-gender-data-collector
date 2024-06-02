from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QFont
from pdf_viewer import PDFViewer
from fpdf import FPDF
from data_utils import getAgeDistributionPlot, getAgeWithGenderPlot

import sys

pdf = FPDF(format="A4")
pdf.add_page()
pdf.set_font('Helvetica', size=48)
pdf.cell(text="Report")
pdf.add_page()
pdf.image(getAgeDistributionPlot(), w=200,
          title="IMAGEEE", keep_aspect_ratio=True)
pdf.add_page()
pdf.image(getAgeWithGenderPlot(), w=200, keep_aspect_ratio=True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("SegoeUI", 12))
    window = QMainWindow()
    pdfViewer = PDFViewer(window)

    pdfViewer.openBytePDF(pdf.output())
    window.setCentralWidget(pdfViewer)
    window.show()
    app.exec()
