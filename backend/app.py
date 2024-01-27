import sys
from main import main
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets

app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
widget.setFixedHeight(700)
widget.setFixedWidth(1300)
mainwindow = main(widget=widget)
widget.addWidget(mainwindow)
widget.show()
sys.exit(app.exec_())