import pandas as pd
from datetime import datetime, timedelta
from DataBase import DataBase

class subtract_dates_and_time():
    @staticmethod
    def hours(number):
        try:
            return (datetime.today() - timedelta(hours=number)).strftime('%Y/%m/%d')
        except:
            return number

    @staticmethod
    def days(number):
        try:
            return (datetime.today() - timedelta(days=number)).strftime('%Y/%m/%d')
        except:
            return number
            
    @staticmethod
    def months(number):
        try:
            return (datetime.today() - timedelta(months=number)).strftime('%Y/%m/%d')
        except:
            return number
        

class wrangle_data():
    def __init__(self):
        self.data_base_connection = DataBase.connect_data_base()

    def wrangle(self,data_frame,save=True,category="buy"):
        """
        wrangle the data 
        category - buy : properties for sale
                 - rent : properties for rent
                 - commertial : commertial properties
        
        """
        subtraction = subtract_dates_and_time()
        
        if category == "rent" or category == "commertial":
            data_frame["Rent Type"] = data_frame.Price.apply(lambda price: price.replace(",","").split(' ')[-1].replace('EGP/', ''))
            
            

        data_frame["price"] = data_frame.Price.apply(lambda price: "Ask for price" if price == "Ask for price" else float(price[:-4].replace(",","").replace(" EGP/m","")))  

        data_frame["bedrooms"] = pd.to_numeric(data_frame.bed_bath_area.apply(lambda bed_bath_area_list: bed_bath_area_list[0] if len(bed_bath_area_list) == 3 else "").str.replace('+', '').replace('studio','1'),downcast='integer')

        data_frame["bathrooms"] = pd.to_numeric(data_frame.bed_bath_area.apply(lambda bed_bath_area_list: bed_bath_area_list[1] if len(bed_bath_area_list) == 3 else "").str.replace('+', ''),downcast='integer')

        data_frame["area"] = pd.to_numeric(data_frame.bed_bath_area.apply(lambda bed_bath_area_list: bed_bath_area_list[2].split(" ")[0].replace("+", "").replace(",", "") if len(bed_bath_area_list) == 3 else bed_bath_area_list[-1].split(" ")[0].replace("+", "").replace(",", "")),downcast='integer')

        data_frame["provider"] = data_frame.provider.str.replace(' logo image', '')

        data_frame['Posting Time'] = data_frame['Posting Time'].str.replace('Listed | ago', '').str.replace("more than ","").str.replace("+","")
        data_frame['Posting Time'] = data_frame['Posting Time'].apply(lambda posting_time: subtraction.days(int(posting_time.split(" ")[0]))
            if "days" or "day" in posting_time
            else (subtraction.months(int(posting_time.split(" ")[0]))
                  if "months" or "month" in posting_time
                  else subtraction.hours(int(posting_time.split(" ")[0]))))

        data_frame["governorate"] = data_frame.Location.apply(lambda governorate: governorate.split(",")[-1])

        data_frame["city"] = data_frame.Location.apply(lambda Location: Location.split(",")[-2])

        wrangled_dataframe = data_frame.drop(columns=["bed_bath_area", "Price"])
        
        if save:
            if_exists = 'append'
            
            wrangled_dataframe.index += 1
            
            if category == "rent" or category == "commertial":
                rent_types_dataframe = wrangled_dataframe['Rent Type'].drop_duplicates().reset_index().drop('index', axis=1).reset_index().rename(columns={'index': f'Rent Type ID'})
                rent_types_dataframe.to_sql(f'{category}_rent_types_id', self.data_base_connection, if_exists=if_exists, index=False)
                print("rent types added to DB with : ", if_exists)

            providers_dataframe = wrangled_dataframe['provider'].drop_duplicates().reset_index().drop('index', axis=1).reset_index().rename(columns={'index': 'Provider ID'})
            providers_dataframe.to_sql(f'{category}_providers_id', self.data_base_connection, if_exists=if_exists, index=False)
            print("providers added to DB with : ", if_exists)

            locations_dataframe = wrangled_dataframe['Location'].drop_duplicates().reset_index().drop('index', axis=1).reset_index().rename(columns={'index': 'Location ID'})
            locations_dataframe.to_sql(f'{category}_locations_id', self.data_base_connection, if_exists=if_exists, index=False)
            print("Locations added to DB with : ", if_exists)
            
            if category == "rent" or category == "commertial":
                fact_dataframe = pd.DataFrame({
                "Property ID": range(1, len(wrangled_dataframe) + 1),
                "Price": wrangled_dataframe['price'],
                "Description": wrangled_dataframe['Description'],
                "Bedrooms": wrangled_dataframe['bedrooms'],
                "Bathrooms": wrangled_dataframe['bathrooms'],
                "City": wrangled_dataframe["city"],
                "Area": wrangled_dataframe['area'],
                "Governorate": wrangled_dataframe["governorate"],
                "Posting Time": wrangled_dataframe['Posting Time'],
                "Property Type": wrangled_dataframe['Property Type'],
                "Provider ID": wrangled_dataframe['provider'].apply(lambda provider_id: providers_dataframe[providers_dataframe['provider'] == provider_id]['Provider ID'].values[0]),
                "Location ID": wrangled_dataframe['Location'].apply(lambda location_id: locations_dataframe[locations_dataframe['Location'] == location_id]['Location ID'].values[0]),
                "Rent Type ID": wrangled_dataframe['Rent Type'].apply(lambda rent_type_id: rent_types_dataframe[rent_types_dataframe['Rent Type'] == rent_type_id]['Rent Type ID'].values[0])})
                
            else:
                fact_dataframe = pd.DataFrame({
                    "Property ID": range(1, len(wrangled_dataframe) + 1),
                    "Price": wrangled_dataframe['price'],
                    "Description": wrangled_dataframe['Description'],
                    "Bedrooms": wrangled_dataframe['bedrooms'],
                    "Bathrooms": wrangled_dataframe['bathrooms'],
                    "Area": wrangled_dataframe['area'],
                    "Governorate": wrangled_dataframe["governorate"],
                    "City": wrangled_dataframe["city"],
                    "URLS": wrangled_dataframe["url"],
                    "Posting Time": wrangled_dataframe['Posting Time'],
                    "Property Type": wrangled_dataframe['Property Type'],
                    "Provider ID": wrangled_dataframe['provider'].apply(lambda provider: providers_dataframe[providers_dataframe['provider'] == provider]['Provider ID'].values[0]),
                    "Location ID": wrangled_dataframe['Location'].apply(lambda location: locations_dataframe[locations_dataframe['Location'] == location]['Location ID'].values[0])})

            fact_dataframe.to_sql(f'{category}_fact_table', self.data_base_connection, if_exists=if_exists, index=False)
            print(f"{category} fact table added in DB with : ", if_exists)
            print("\n")
            if category == "rent" or category == "commertial":
                print(f"""data frames added to database:
                      {category}_rent_types_id
                      {category}_providers_id
                      {category}_locations_id
                      {category}_fact_table""")
            else:
                print(f"""data frames added to database:
                      {category}_providers_id
                      {category}_locations_id
                      {category}_fact_table""")

        return wrangled_dataframe
        