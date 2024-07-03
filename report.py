import pandas as pd

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow

from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import matplotlib.pyplot as plt

from DataBase import DataBase


class report(QMainWindow):

    def __init__(self,widget):
        super(report,self).__init__()

        self.data_base_connection = DataBase.connect_data_base()

        dirname = "./UIs/report.ui"

        loadUi(dirname, self)

        self.widget = widget

        self.report_buy.clicked.connect(self.report_buy_func)
        self.report_rent.clicked.connect(self.report_rent_func)
        self.report_Commertial.clicked.connect(self.report_Commertial_func)

    def report_buy_func(self):
        data_frame = pd.read_sql(con=self.data_base_connection,sql="""SELECT * FROM buy_fact_table as bft
INNER JOIN buy_locations_id as bl ON bft.'Location ID' = bl.'Location ID'
INNER JOIN buy_providers_id as bp ON bft.'Provider ID' = bp.'Provider ID'
""").set_index("Property ID").drop(columns=["Provider ID","Location ID"]).drop_duplicates()

        data_frame.Price = data_frame.Price.apply(lambda x: 0 if x == "Ask for price" else x)
        data_frame.Price = data_frame.Price.astype(float)

        with PdfPages('./Reports/buy_report.pdf') as pdf_pages:
            figu = plt.figure(0,figsize=(20,10))
            ax = plt.gca()
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
            plt.xticks(rotation=90)
            sns.countplot(ax=ax, y="City", data=data_frame).set(title='Number of properties sold in cities')
            pdf_pages.savefig(figu)

            figu = plt.figure(1,figsize=(20,10))
            ax = plt.gca()
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
            plt.ticklabel_format(style='plain')
            sns.scatterplot(ax=ax, hue="Property Type", x="Price", y="Area", data=data_frame).set(title='price area and type of properties')
            pdf_pages.savefig(figu)

            figu = plt.figure(2,figsize=(20,10))
            ax = plt.gca()
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
            plt.ticklabel_format(style='plain')
            sns.barplot(ax=ax, y="Property Type", x="Price", hue="Governorate", data=data_frame).set(title='property type and price in governorates')
            pdf_pages.savefig(figu)

        self.report_status.setText("Report Saved in the resources file")
        self.report_file.setText("buy_report.pdf")


    def report_rent_func(self):
        data_frame = pd.read_sql(con=self.data_base_connection,sql="""SELECT * FROM rent_fact_table as rft
INNER JOIN rent_locations_id as rl ON rft.'Location ID' = rl.'Location ID'
INNER JOIN rent_providers_id as rp ON rft.'Provider ID' = rp.'Provider ID'
INNER JOIN rent_rent_types_id as rt ON rft.'Rent Type Id' = rt.'Rent Type Id'
""").set_index("Property ID").drop(columns=["Provider ID","Location ID"]).drop_duplicates()

        data_frame.Price = data_frame.Price.apply(lambda x: 0 if x == "Ask for price" else x)
        data_frame.Price = data_frame.Price.astype(float)

        with PdfPages('./Reports/rent_report.pdf') as pdf_pages:
            figu = plt.figure(0, figsize=(20, 10))
            ax = plt.gca()
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
            plt.xticks(rotation=90)
            sns.countplot(ax=ax, y="City",hue="Rent Type", data=data_frame).set(title='Number of properties rented in cities')
            pdf_pages.savefig(figu)

            figu = plt.figure(1, figsize=(20, 10))
            ax = plt.gca()
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
            plt.ticklabel_format(style='plain')
            sns.scatterplot(ax=ax, hue="Property Type", x="Price", y="Area", data=data_frame).set(title='price area and type of properties')
            pdf_pages.savefig(figu)

            figu = plt.figure(2, figsize=(20, 10))
            ax = plt.gca()
            ax.get_xaxis().get_major_formatter().set_useOffset(False)

            sns.barplot(ax=ax, y="Property Type", x="Price", hue="Governorate", data=data_frame).set(title='property type and price in governorates')
            pdf_pages.savefig(figu)

            self.report_status.setText("Report Saved in the resources file")
            self.report_file.setText("rent_report.pdf")


    def report_Commertial_func(self):
        data_frame = pd.read_sql(con=self.data_base_connection, sql="""SELECT * FROM commertial_fact_table as rft
INNER JOIN commertial_locations_id as rl ON rft.'Location ID' = rl.'Location ID'
INNER JOIN commertial_providers_id as rp ON rft.'Provider ID' = rp.'Provider ID'
INNER JOIN commertial_rent_types_id as rt ON rft.'Rent Type Id' = rt.'Rent Type Id'
""").set_index("Property ID").drop(columns=["Provider ID","Location ID","Rent Type ID"]).drop_duplicates()

        data_frame.Price = data_frame.Price.apply(lambda x: 0 if x == "Ask for price" else x)
        data_frame.Price = data_frame.Price.astype(float)

        with PdfPages('./Reports/com_report.pdf') as pdf_pages:
            figu = plt.figure(0, figsize=(20, 10))
            ax = plt.gca()
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
            plt.xticks(rotation=90)
            sns.countplot(ax=ax, y="City", hue="Rent Type", data=data_frame).set(title='Number of properties rented in cities')
            pdf_pages.savefig(figu)

            figu = plt.figure(1, figsize=(20, 10))
            ax = plt.gca()
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
            plt.ticklabel_format(style='plain')
            sns.scatterplot(ax=ax, hue="Property Type", x="Price", y="Area", data=data_frame).set(title='price area and type of properties')
            pdf_pages.savefig(figu)

            figu = plt.figure(2, figsize=(20, 10))
            ax = plt.gca()
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
            sns.barplot(ax=ax, y="Property Type", x="Price", hue="Governorate", data=data_frame).set(title='property type and price in governorates')
            pdf_pages.savefig(figu)

            self.report_status.setText("Report Saved in the resources file")
            self.report_file.setText("com_report.pdf")