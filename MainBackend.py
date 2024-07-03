import pandas as pd
from datetime import date

from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox
from PyQt5.uic import loadUi
from report import report

from DataBase import DataBase
from ChromeDriver import chrome_driver
from CollectData import CollectData
from WrangleData import wrangle_data

class main(QMainWindow):

    def __init__(self,widget):
        super(main,self).__init__()

        dirname = "./UIs/PropertyPulseAnalyzermain.ui"

        loadUi(dirname, self)

        self.widget = widget
        
        self.data_base_connection = DataBase.connect_data_base()
        self.setWindowTitle("Property Pulse Analyzer")

        f = open("./DataBase/last_data_edit_time.txt", "r")

        self.date.setText(str(date.today()))
        self.last_date_edited.setText(str(f.read()))


        self.get_data_btn.clicked.connect(self.get_data)
        self.show_buy_btn.clicked.connect(self.show_buy)
        self.show_rent_btn.clicked.connect(self.show_rent)
        self.show_commertial_btn.clicked.connect(self.show_commertial)
        self.analysis_report_btn.clicked.connect(self.open_analysis_report)


    def get_data(self):
        try:
            driver = chrome_driver()
            
            self.buy_wrangled_data = wrangle_data().wrangle(CollectData(driver,int(self.pages.text())).get_data(category='buy')
                                                            ,save=True,category="buy")
            
            self.rent_wrangled_data = wrangle_data().wrangle(CollectData(driver,int(self.pages.text())).get_data(category='rent')
                                                             ,save=True,category="rent")
            
            self.commertial_wrangled_data = wrangle_data().wrangle(CollectData(driver,int(self.pages.text())).get_data(category='commertial')
                                                                   ,save=True,category="commertial")
            
            driver.close()
            

            f = open("./DataBase/last_data_edit_time.txt", "w").write(f"{str(date.today())}")
            self.last_date_edited.setText(str(str(date.today())))

        except Exception as e:
            error_dialog = QMessageBox()
            error_dialog.setWindowTitle("Empty pages section")
            error_dialog.setText("write number of pages in numbers!")
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.exec_()

    def show_buy(self):
        rows_number = len(self.buy_wrangled_data.index)
        self.tableWidget.setColumnCount(len(self.buy_wrangled_data.columns))
        self.tableWidget.setRowCount(rows_number)
        self.tableWidget.setHorizontalHeaderLabels(self.buy_wrangled_data.columns)

        for i in range(rows_number):
            for j in range(len(self.buy_wrangled_data.columns)):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(self.buy_wrangled_data.iat[i, j])))

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def show_rent(self):
        rows_number = len(self.rent_wrangled_data.index)
        self.tableWidget.setColumnCount(len(self.rent_wrangled_data.columns))
        self.tableWidget.setRowCount(rows_number)
        self.tableWidget.setHorizontalHeaderLabels(self.rent_wrangled_data.columns)

        for i in range(rows_number):
            for j in range(len(self.rent_wrangled_data.columns)):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(self.rent_wrangled_data.iat[i, j])))

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def show_commertial(self):
        rows_number = len(self.commertial_wrangled_data.index)
        self.tableWidget.setColumnCount(len(self.commertial_wrangled_data.columns))
        self.tableWidget.setRowCount(rows_number)
        self.tableWidget.setHorizontalHeaderLabels(self.commertial_wrangled_data.columns)

        for i in range(rows_number):
            for j in range(len(self.commertial_wrangled_data.columns)):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(self.commertial_wrangled_data.iat[i, j])))

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def open_analysis_report(self):
        mainpage = report(widget=self.widget)
        self.widget.addWidget(mainpage)
        self.widget.setCurrentIndex(self.widget.currentIndex() + 1)