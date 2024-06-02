from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import *
from PyQt6.QtCharts import *
from PyQt6.QtGui import *
from PyQt6.QtCore import QThread
from datetime import datetime
from fpdf import FPDF

from data_utils import *
from pdf_viewer import PDFViewer
from logger import logger

plot_funcs = [
    getAgesPiePlot,
    getGendersPiePlot,
    getAgeWithGenderPlot,
    getAgeDistributionPlot,
    getCountByDateHist,
    getCountWithGenderByDateHist,
    getCountWithAgeByDateHist
]


class ReportPDF(FPDF):
    def header(self) -> None:
        self.set_font("helvetica", "B", 15)
        self.cell(0, 10, "Age & Gender Data Report", border=1, align="C")
        self.ln(20)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


class ReportWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super(ReportWindow, self).__init__(parent)

        self.mainLayout = QHBoxLayout()
        self.container = QWidget()
        self.chartLayout = QVBoxLayout()

        self.mainLayout.addLayout(self.chartLayout)
        self.container.setLayout(self.mainLayout)
        if len(db.fetchAll()) != 0:
            self.addPdfView()

            # Add charts
            self.genderChartThread = QThread(self)
            self.genderChartThread.started.connect(self.addGenderChart)
            self.genderChartThread.start()

            self.ageChartThread = QThread(self)
            self.ageChartThread.started.connect(self.addAgeChart)
            self.ageChartThread.start()

            self.mainLayout.addWidget(self.pdfViewer)

        self.setCentralWidget(self.container)

    def addGenderChart(self):
        self.genderSeries = QPieSeries()
        for i in getGenders().items():
            self.genderSeries.append(i[0], i[1])

        [i.setLabelVisible(True) for i in self.genderSeries.slices()]
        for i in self.genderSeries.slices():
            if i.label() == "Female":
                i.setColor(QColor("#FDB0C0"))
            elif i.label() == "Male":
                i.setColor(QColor("#6488EA"))

        self.genderChart = QChart()
        self.genderChart.addSeries(self.genderSeries)
        self.genderChart.setTitle('Genders Chart')
        self.genderChart.setAnimationOptions(
            QChart.AnimationOption.AllAnimations)
        self.genderChart.layout().setContentsMargins(0, 0, 0, 0)

        self.genderChartView = QChartView(self.genderChart)
        self.genderChartView.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.genderChartView.setMinimumSize(100, 100)
        self.chartLayout.addWidget(self.genderChartView)

        logger.info("Gender chart added")

    def addAgeChart(self):
        self.ageSeries = QPieSeries()
        for i in getAges().items():
            self.ageSeries.append(i[0], i[1])
        [i.setLabelVisible(True)
         for i in self.ageSeries.slices() if i.value() != 0]

        self.ageChart = QChart()
        self.ageChart.addSeries(self.ageSeries)
        self.ageChart.setTitle('Ages Chart')
        self.ageChart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        self.ageChart.layout().setContentsMargins(0, 0, 0, 0)

        self.ageChartView = QChartView(self.ageChart)
        self.ageChartView.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.ageChartView.setMinimumSize(100, 100)
        self.chartLayout.addWidget(self.ageChartView)

        logger.info("Age chart added")

    def addPdfView(self):
        pdf = ReportPDF()
        pdf.add_page()
        dInfo = getDataInfo()
        pdf.set_font("helvetica", size=14)
        pdf.cell(text=f"Total Record: {dInfo.get('totalRecord')}")
        pdf.ln(9)
        pdf.cell(text=f"Male: {dInfo.get('maleCount')}")
        pdf.ln(9)
        pdf.cell(text=f"Female: {dInfo.get('femaleCount')}")
        pdf.ln(9)
        pdf.cell(text=f"START: {dInfo.get('firstRecord')}")
        pdf.ln(9)
        pdf.cell(text=f"END: {dInfo.get('lastRecord')}")
        pdf.ln(27)
        pdf.cell(
            text=f"This pdf is auto generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        pdf.add_page()
        for f in plot_funcs:
            plot = f()
            pdf.image(plot, w=pdf.epw, keep_aspect_ratio=True)
            pdf.ln(4)
        logger.info("Report PDF generated")

        self.pdfViewer = PDFViewer(self)
        self.pdfViewer.openBytePDF(pdf.output())

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        if self.genderChartThread.isRunning():
            self.genderChartThread.terminate()
        if self.ageChartThread.isRunning():
            self.ageChartThread.terminate()
        a0.accept()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    winodw = ReportWindow()
    winodw.showMaximized()
    app.exec()
