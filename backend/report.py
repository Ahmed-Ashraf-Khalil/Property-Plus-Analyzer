from database.database import DB
import pandas as pd
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QApplication, QMessageBox
from pyqt5_plugins.examplebuttonplugin import QtGui
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib


class report(QMainWindow):

    def __init__(self,widget):
        super(report,self).__init__()

        self.widget = widget

        #database connection
        self.conn = DB.db_connect()

        dirname = "../uis/report.ui"

        loadUi(dirname, self)

        self.rep_buy.clicked.connect(self.rep_buy_func)
        self.rep_rent.clicked.connect(self.rep_rent_func)
        self.rep_com.clicked.connect(self.rep_com_func)

    def rep_buy_func(self):
        df = pd.read_sql(con=self.conn,sql="""SELECT * FROM buy_df""")
        df.price = df.price.apply(lambda x: 0 if x == "Ask for price" else x)
        df.price = df.price.astype(float)

        with PdfPages('../reports/buy_report.pdf') as pdf_pages:
            figu = plt.figure(0,figsize=(20,10))
            ax = plt.gca()
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
            plt.xticks(rotation=90)
            sns.countplot(ax=ax, y="city", data=df).set(title='Number of properties sold in cities')
            pdf_pages.savefig(figu)

            figu = plt.figure(1,figsize=(20,10))
            ax = plt.gca()
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
            plt.ticklabel_format(style='plain')
            sns.scatterplot(ax=ax, hue="Property Type", x="price", y="area", data=df).set(title='price area and type of properties')
            pdf_pages.savefig(figu)

            figu = plt.figure(2,figsize=(20,10))
            ax = plt.gca()
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
            plt.ticklabel_format(style='plain')
            sns.barplot(ax=ax, y="Property Type", x="price", hue="governorate", data=df).set(title='property type and price in governorates')
            pdf_pages.savefig(figu)

        self.rep_status.setText("Report Saved in the resources file")
        self.rep_file.setText("buy_report.pdf")


    def rep_rent_func(self):
        df = pd.read_sql(con=self.conn,sql="""SELECT * FROM rent_df""")
        df.price = df.price.apply(lambda x: 0 if x == "Ask for price" else x)
        df.price = df.price.astype(float)

        with PdfPages('../reports/rent_report.pdf') as pdf_pages:
            figu = plt.figure(0, figsize=(20, 10))
            ax = plt.gca()
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
            plt.xticks(rotation=90)
            sns.countplot(ax=ax, y="city",hue="Rent Type", data=df).set(title='Number of properties rented in cities')
            pdf_pages.savefig(figu)

            figu = plt.figure(1, figsize=(20, 10))
            ax = plt.gca()
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
            plt.ticklabel_format(style='plain')
            sns.scatterplot(ax=ax, hue="Property Type", x="price", y="area", data=df).set(
                title='price area and type of properties')
            pdf_pages.savefig(figu)

            figu = plt.figure(2, figsize=(20, 10))
            ax = plt.gca()
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
            #plt.ticklabel_format(style='plain')
            sns.barplot(ax=ax, y="Property Type", x="price", hue="governorate", data=df).set(
                title='property type and price in governorates')
            pdf_pages.savefig(figu)

            self.rep_status.setText("Report Saved in the resources file")
            self.rep_file.setText("rent_report.pdf")


    def rep_com_func(self):
        df = pd.read_sql(con=self.conn, sql="""SELECT * FROM com_df""")
        df.price = df.price.apply(lambda x: 0 if x == "Ask for price" else x)
        df.price = df.price.astype(float)

        with PdfPages('../reports/com_report.pdf') as pdf_pages:
            figu = plt.figure(0, figsize=(20, 10))
            ax = plt.gca()
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
            plt.xticks(rotation=90)
            sns.countplot(ax=ax, y="city", hue="Rent Type", data=df).set(title='Number of properties rented in cities')
            pdf_pages.savefig(figu)

            figu = plt.figure(1, figsize=(20, 10))
            ax = plt.gca()
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
            plt.ticklabel_format(style='plain')
            sns.scatterplot(ax=ax, hue="Property Type", x="price", y="area", data=df).set(
                title='price area and type of properties')
            pdf_pages.savefig(figu)

            figu = plt.figure(2, figsize=(20, 10))
            ax = plt.gca()
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
            #plt.ticklabel_format(style='plain')
            sns.barplot(ax=ax, y="Property Type", x="price", hue="governorate", data=df).set(
                title='property type and price in governorates')
            pdf_pages.savefig(figu)

            self.rep_status.setText("Report Saved in the resources file")
            self.rep_file.setText("com_report.pdf")