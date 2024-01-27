import pandas as pd
from datetime import date
from backend import collect
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox
from PyQt5.uic import loadUi
from database.database import DB
from report import report


class main(QMainWindow):

    def __init__(self,widget):
        super(main,self).__init__()


        #database connection
        self.conn = DB.db_connect()

        dirname = "../uis/PropertyPulseAnalyzermain.ui"

        loadUi(dirname, self)

        self.widget = widget

        # set the title
        self.setWindowTitle("Property Pulse Analyzer")

        f = open("../database/last_data_edit_time.txt", "r")

        self.date.setText(str(date.today()))
        self.addedlastdate.setText(str(f.read()))


        self.getdatabtn.clicked.connect(self.getdatafunc)
        self.buybtn.clicked.connect(self.buyfunc)
        self.rentbtn.clicked.connect(self.rentfunc)
        self.combtn.clicked.connect(self.comfunc)
        self.analysisreportbtn.clicked.connect(self.analysisreportfunc)


    def getdatafunc(self):
        try:
            collect.collect_data(pages=int(self.pages.text())).collect_buy()
            collect.collect_data(pages=int(self.pages.text())).collect_rent()
            collect.collect_data(pages=int(self.pages.text())).collect_com()

            f = open("../database/last_data_edit_time.txt", "w").write(f"{str(date.today())}")
            self.addedlastdate.setText(str(str(date.today())))

        except Exception as e:
            error_dialog = QMessageBox()
            error_dialog.setWindowTitle("Empty pages section")
            error_dialog.setText("write number of pages in numbers!")
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.exec_()

    def buyfunc(self):
        df_buy = pd.read_sql(con=self.conn,sql="""SELECT * FROM buy_df""")
        NumRows = len(df_buy.index)
        self.tableWidget.setColumnCount(len(df_buy.columns))
        self.tableWidget.setRowCount(NumRows)
        self.tableWidget.setHorizontalHeaderLabels(df_buy.columns)

        for i in range(NumRows):
            for j in range(len(df_buy.columns)):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(df_buy.iat[i, j])))

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def rentfunc(self):
        df_rent = pd.read_sql(con=self.conn,sql="""SELECT * FROM rent_df""")
        NumRows = len(df_rent.index)
        self.tableWidget.setColumnCount(len(df_rent.columns))
        self.tableWidget.setRowCount(NumRows)
        self.tableWidget.setHorizontalHeaderLabels(df_rent.columns)

        for i in range(NumRows):
            for j in range(len(df_rent.columns)):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(df_rent.iat[i, j])))

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def comfunc(self):
        df_com = pd.read_sql(con=self.conn,sql="""SELECT * FROM com_df""")
        NumRows = len(df_com.index)
        self.tableWidget.setColumnCount(len(df_com.columns))
        self.tableWidget.setRowCount(NumRows)
        self.tableWidget.setHorizontalHeaderLabels(df_com.columns)

        for i in range(NumRows):
            for j in range(len(df_com.columns)):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(df_com.iat[i, j])))

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def analysisreportfunc(self):
        mainpage = report(widget=self.widget)
        self.widget.addWidget(mainpage)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)