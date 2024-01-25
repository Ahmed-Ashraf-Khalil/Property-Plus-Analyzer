import sys
from PyQt5.QtWidgets import QApplication
from pyqt5_plugins.examplebutton import QtWidgets

from main import main


app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
widget.setFixedHeight(700)
widget.setFixedWidth(1300)
mainwindow = main(widget=widget)
widget.addWidget(mainwindow)
widget.show()
sys.exit(app.exec_())