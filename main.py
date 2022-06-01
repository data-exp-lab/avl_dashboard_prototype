"""Something."""
import random
import sys
import matplotlib

matplotlib.use("Qt5Agg")

from PyQt5 import QtCore, QtWidgets, QtWebEngineCore, QtWebEngineWidgets, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class QtSchemeHandler(QtWebEngineCore.QWebEngineUrlSchemeHandler):
    def requestStarted(self, job):
        request_url = job.requestUrl()
        request_path = request_url.path()
        file = QtCore.QFile("." + request_path)
        file.setParent(job)
        job.destroyed.connect(file.deleteLater)
        file_info = QtCore.QFileInfo(file)
        mime_database = QtCore.QMimeDatabase()
        mime_type = mime_database.mimeTypeForFile(file_info)
        job.reply(mime_type.name().encode(), file)


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QWidget):
    counter = 0

    def __init__(self, screen):
        super(MainWindow, self).__init__()
        self.screen = screen
        self.setStyleSheet("background-color: blue;")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.verticalLayout)
        self.browser = QtWebEngineWidgets.QWebEngineView()
        self.scheme_handler = QtSchemeHandler()
        self.browser.page().setBackgroundColor(QtCore.Qt.GlobalColor.transparent)
        self.browser.page().profile().installUrlSchemeHandler(
            b"qt", self.scheme_handler
        )
        url = QtCore.QUrl("qt://main")
        url.setPath("/index.html")
        self.browser.load(url)
        self.verticalLayout.addWidget(self.browser)

        self.mpl_canvas = MplCanvas(self, width=5, height=4, dpi=100)
        n = 50
        self.xdata = list(range(n))
        self.ydata = [random.randint(0, 10) for i in range(n)]
        self.update_plot()
        self.verticalLayout.addWidget(self.mpl_canvas)

        self.browser.loadFinished.connect(self.show)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        self.ydata = self.ydata[1:] + [random.randint(0, 10)]
        self.mpl_canvas.axes.cla()
        self.mpl_canvas.axes.plot(self.xdata, self.ydata, "r")
        self.mpl_canvas.draw()
        QtGui.QScreen.grabWindow(self.screen, self.window().winId()).save(
            f"foo_{self.counter:03}.png", "png", -1
        )
        self.counter += 1


if __name__ == "__main__":
    scheme = QtWebEngineCore.QWebEngineUrlScheme(b"qt")
    scheme.setFlags(QtWebEngineCore.QWebEngineUrlScheme.CorsEnabled)
    QtWebEngineCore.QWebEngineUrlScheme.registerScheme(scheme)
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(app.primaryScreen())
    sys.exit(app.exec_())
