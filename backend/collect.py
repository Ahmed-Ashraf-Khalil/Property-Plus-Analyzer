from datetime import datetime, timedelta
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from pandas import DataFrame
import pandas as pd
from database.database import DB


# pass cloudflare are you a robot (yes i am)
def pass_cloudflare():
    # apply chrome options
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationCintrolled")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")
    #    options.add_argument("--auto-open-devtools-for-tabs")

    # set the driver to use
    driver = webdriver.Chrome(options=options)

    time.sleep(3)

    return driver
class subtract_dates_and_time():
    def __init__(self):
        pass

    def hours_minus(num):
        # subtract hours
        return (datetime.today() - timedelta(hours=num)).strftime('%Y/%m/%d')

    def days_minus(num):
        # subtract days
        return (datetime.today() - timedelta(days=num)).strftime('%Y/%m/%d')

    def months_minus(num):
        # subtract months
        return (datetime.today() - timedelta(months=num)).strftime('%Y/%m/%d')


class collect_data():
    def __init__(self,pages=1):
        self.conn = DB.db_connect()
        self.driver = pass_cloudflare()
        self.pages = pages

        # maximize window
        self.driver.maximize_window()

    # ---------------------------------------------- buy data ----------------------------------------------------------
    def collect_buy(self,save=True):

        # Extract property data
        property_data = []

        # Iterate over pages
        for i in range(self.pages):

            # Set the target URL
            url = f"https://www.propertyfinder.eg/en/buy/properties-for-sale.html?page={i + 1}"

            # Load the target URL
            self.driver.get(url)

            # property_elements = driver.find_elements(By.XPATH, "//div[@class='property-card-module_property-card__Yuso0 property-card-module_property-card--DESKTOP__7At5L ']")

            property_elements = self.driver.find_elements(By.XPATH, "//li[contains(@data-testid, 'list-item-')]")
            for property_element in property_elements:
                try:
                    # Extract property type
                    property_type_element = property_element.find_element(By.XPATH,
                                                                          ".//p[@data-testid='property-card-type']")
                    property_type = property_type_element.text.strip()

                    # Extract price
                    price_element = property_element.find_element(By.XPATH, ".//p[@data-testid='property-card-price']")
                    price = price_element.text.strip()

                    # Extract description
                    description_element = property_element.find_element(By.XPATH,
                                                                        ".//h2[@class='styles-module_content__title__eOEkd']")
                    description = description_element.text.strip()

                    # Extract location
                    location_element = property_element.find_element(By.XPATH,
                                                                     ".//div[@data-testid='property-card-location']")
                    location = location_element.text.strip()

                    # Extract number of bedrooms
                    # bedrooms_element = property_element.find_element(By.XPATH, ".//p[@data-testid='property-card-spec-bedroom']")

                    bd_ba_ar_element = property_element.find_element(By.XPATH,
                                                                     ".//div[@data-testid='property-card-details']")
                    bd_ba_ar = bd_ba_ar_element.text.split("\n")

                    # Extract posting time
                    posting_time_element = property_element.find_element(By.XPATH,
                                                                         ".//p[@class='styles-module_footer__publish-info__UVabq']")
                    posting_time = posting_time_element.text.strip()

                    # Extract provider
                    try:
                        provider_container_element = property_element.find_element(By.XPATH,
                                                                                   ".//div[@data-testid='property-card-broker-logo']")
                        provider_element = provider_container_element.find_element(By.XPATH,
                                                                                   ".//img[@data-testid='gallery-picture']")
                        provider = provider_element.get_attribute('title')
                    except:
                        provider = ''

                    # Extract URL
                    url_element = property_element.find_element(By.XPATH,
                                                                ".//a[@class='property-card-module_property-card__link__L6AKb']")
                    url = url_element.get_attribute('href')

                    # Append extracted data to property data list
                    property_data.append({
                        "Property Type": property_type,
                        "Price": price,
                        "Description": description,
                        "Location": location,
                        "bed_bath_area": bd_ba_ar,
                        "Posting Time": posting_time,
                        "provider": provider,
                        "url": url
                    })
                except StaleElementReferenceException:
                    # Handle stale element exceptions due to dynamic page updates
                    pass

        # Create a Pandas DataFrame from the extracted property data
        df = DataFrame(property_data)

        # ----------------------------------------- wrangle buy data ---------------------------------------------------

        # set the object of subtracting dates
        sub = subtract_dates_and_time()

        # wrangle price column
        df["price"] = df.Price.apply(lambda a: "Ask for price" if a == "Ask for price" else float(a[:-4].replace(",","")))  # price

        # wrangle bedrooms column
        df["bedrooms"] = pd.to_numeric(
            df.bed_bath_area.apply(lambda x: x[0] if len(x) == 3 else "").str.replace('+', '').replace('studio',
                                                                                                       '1'),
            downcast='integer')  # bedrooms

        # wrangle bathrooms column
        df["bathrooms"] = pd.to_numeric(
            df.bed_bath_area.apply(lambda x: x[1] if len(x) == 3 else "").str.replace('+', ''),
            downcast='integer')  # bathrooms

        # wrangle area column
        df["area"] = pd.to_numeric(df.bed_bath_area.apply(
            lambda x: x[2].split(" ")[0].replace("+", "").replace(",", "") if len(x) == 3 else x[-1].split(" ")[0].replace("+", "").replace(",", "")),
            downcast='integer')  # area

        # wrangle provider column
        df["provider"] = df.provider.str.replace(' logo image', '')  # provider

        # wrangle posting time column
        df['Posting Time'] = df['Posting Time'].str.replace('Listed | ago', '').str.replace("more than ",
                                                                                              "").str.replace("+",
                                                                                                              "")

        df['Posting Time'] = df['Posting Time'].apply(
            lambda x: subtract_dates_and_time.days_minus(int(x.split(" ")[0]))
            if "days" or "day" in x
            else (subtract_dates_and_time.months_minus(int(x.split(" ")[0]))
                  if "months" or "month" in x
                  else subtract_dates_and_time.hours_minus(int(x.split(" ")[0]))))

        # wrangle location column to governorate and city columns
        df["governorate"] = df.Location.apply(lambda x: x.split(",")[-1])

        df["city"] = df.Location.apply(lambda x: x.split(",")[-2])

        # drop unnecessary columns
        df.drop(columns=["bed_bath_area", "Price"], inplace=True)

        # ------------------------------------ database save -----------------------------------------------------------
        if save:
            if_exists = 'replace'

            df.index += 1

            # fact tables
            # property type
            property_types_df = df['Property Type'].drop_duplicates().reset_index().drop('index',
                                                                                         axis=1).reset_index().rename(
                columns={'index': 'Property Type ID'})
            property_types_df.to_sql('property_types_buy', self.conn, if_exists=if_exists, index=False)

            print("property types added to DB with : ", if_exists)

            # providers
            providers_df = df['provider'].drop_duplicates().reset_index().drop('index', axis=1).reset_index().rename(
                columns={'index': 'Provider ID'})
            providers_df.to_sql('providers_buy', self.conn, if_exists=if_exists, index=False)

            print("providers added to DB with : ", if_exists)

            # locations
            locations_df = df['Location'].drop_duplicates().reset_index().drop('index', axis=1).reset_index().rename(
                columns={'index': 'Location ID'})
            locations_df.to_sql('locations_buy', self.conn, if_exists=if_exists, index=False)

            print("Locations added to DB with : ", if_exists)

            # posting time
            posting_time_df = df['Posting Time'].drop_duplicates().reset_index().drop('index',
                                                                                      axis=1).reset_index().rename(
                columns={'index': 'Posting Time ID'})
            posting_time_df.to_sql('Posting_Time_buy', self.conn, if_exists=if_exists, index=False)

            print("posting time added to DB with : ", if_exists)

            # Create the fact table
            fact_df = pd.DataFrame({
                "Property ID": range(1, len(df) + 1),
                "Price": df['price'],
                "Description": df['Description'],
                "Bedrooms": df['bedrooms'],
                "Bathrooms": df['bathrooms'],
                "Area": df['area'],
                "Governorate": df["governorate"],
                "City": df["city"],
                "URLS": df["url"],
                "Property Type ID": df['Property Type'].apply(
                    lambda x: property_types_df[property_types_df['Property Type'] == x]['Property Type ID'].values[0]),
                "Provider Id": df['provider'].apply(
                    lambda x: providers_df[providers_df['provider'] == x]['Provider ID'].values[0]),
                "Location ID": df['Location'].apply(
                    lambda x: locations_df[locations_df['Location'] == x]['Location ID'].values[0]),
                "Posting Time ID": df['Posting Time'].apply(
                    lambda x: posting_time_df[posting_time_df['Posting Time'] == x]['Posting Time'].values[0])
            })

            fact_df.to_sql('facts_buy', self.conn, if_exists=if_exists, index=False)
            print("fact_buy table added in DB with : ", if_exists)

            df.to_sql(name ="buy_df",con=self.conn,if_exists=if_exists, index=False)

        # Close the SQLite connection
        self.conn.close()

        # Close the Chrome driver
        self.driver.quit()


    # ---------------------------------------------- rent data ---------------------------------------------------------
    def collect_rent(self,save=True):

        # Extract property data
        property_data = []

        # Iterate over pages
        for i in range(self.pages):

            # Set the target URL
            url = f"https://www.propertyfinder.eg/en/search?c=2&fu=0&rp=m&ob=mr&page={i + 1}"

            # Load the target URL
            self.driver.get(url)

            # property_elements = driver.find_elements(By.XPATH, "//div[@class='property-card-module_property-card__Yuso0 property-card-module_property-card--DESKTOP__7At5L ']")
            property_elements = self.driver.find_elements(By.XPATH, "//li[contains(@data-testid, 'list-item-')]")
            for property_element in property_elements:
                try:
                    # Extract property type
                    property_type_element = property_element.find_element(By.XPATH,
                                                                          ".//p[@data-testid='property-card-type']")
                    property_type = property_type_element.text.strip()

                    # Extract price
                    price_element = property_element.find_element(By.XPATH, ".//p[@data-testid='property-card-price']")
                    price = price_element.text.strip()

                    # Extract description
                    description_element = property_element.find_element(By.XPATH,
                                                                        ".//h2[@class='styles-module_content__title__eOEkd']")
                    description = description_element.text.strip()

                    # Extract location
                    location_element = property_element.find_element(By.XPATH,
                                                                     ".//div[@data-testid='property-card-location']")
                    location = location_element.text.strip()

                    # Extract number of bedrooms
                    bd_ba_ar_element = property_element.find_element(By.XPATH,
                                                                     ".//div[@data-testid='property-card-details']")
                    bd_ba_ar = bd_ba_ar_element.text.split("\n")

                    # Extract posting time
                    posting_time_element = property_element.find_element(By.XPATH,
                                                                         ".//p[@class='styles-module_footer__publish-info__UVabq']")
                    posting_time = posting_time_element.text.strip()

                    # Extract provider
                    try:
                        provider_container_element = property_element.find_element(By.XPATH,
                                                                                   ".//div[@data-testid='property-card-broker-logo']")
                        provider_element = provider_container_element.find_element(By.XPATH,
                                                                                   ".//img[@data-testid='gallery-picture']")
                        provider = provider_element.get_attribute('title')
                    except:
                        provider = ''

                    # Extract URL
                    url_element = property_element.find_element(By.XPATH,
                                                                ".//a[@class='property-card-module_property-card__link__L6AKb']")
                    url = url_element.get_attribute('href')

                    # Append extracted data to property data list
                    property_data.append({
                        "Property Type": property_type,
                        "Price": price,
                        "Description": description,
                        "Location": location,
                        "bed_bath_area": bd_ba_ar,
                        "Posting Time": posting_time,
                        "provider": provider,
                        "url": url
                    })
                except StaleElementReferenceException:
                    # Handle stale element exceptions due to dynamic page updates
                    pass

        # Create a Pandas DataFrame from the extracted property data
        df = DataFrame(property_data)

        # ------------------------------------- wrangle rent -----------------------------------------------------------
        # wrangle rent type
        df["Rent Type"] = df.Price.apply(lambda a: a.replace(",","").split(' ')[-1].replace('EGP/', ''))

        # wrangle price
        df["price"] = df.Price.apply(lambda a: "Ask for price" if a == "Ask for price" else float(a.replace(",","").split(" ")[0]))  # price

        # wrangle bedrooms column
        df["bedrooms"] = pd.to_numeric(
            df.bed_bath_area.apply(lambda x: x[0] if len(x) == 3 else "").str.replace(",","").replace('+', '').replace('studio', '1'),
            downcast='integer')  # bedrooms

        # wrangle bathrooms column
        df["bathrooms"] = pd.to_numeric(
            df.bed_bath_area.apply(lambda x: x[1] if len(x) == 3 else "").str.replace(",","").replace('+', ''),
            downcast='integer')  # bathrooms

        # wrangle area column
        df["area"] = pd.to_numeric(df.bed_bath_area.apply(
            lambda x: x[2].split(" ")[0].replace("+", "").replace(",","") if len(x) == 3 else x[-1].split(" ")[0].replace("+", "").replace(",","")),
                                    downcast='integer')  # area

        # wrangle posting time column
        df['Posting Time'] = df['Posting Time'].str.replace('Listed | ago', '').str.replace("more than ",
                                                                                              "").str.replace("+", "")

        df['Posting Time'] = df['Posting Time'].apply(
            lambda x: subtract_dates_and_time.days_minus(int(x.split(" ")[0]))
            if "days" or "day" in x
            else (subtract_dates_and_time.months_minus(int(x.split(" ")[0]))
                  if "months" or "month" in x
                  else subtract_dates_and_time.hours_minus(int(x.split(" ")[0]))))

        # wrangle provider
        df["provider"] = df.provider.str.replace(' logo image', '')

        # wrangle location column to governorate and city columns
        df["governorate"] = df.Location.apply(lambda x: x.split(",")[-1])

        # wrangle city
        df["city"] = df.Location.apply(lambda x: x.split(",")[-2])

        # drop unnecessary columns
        df.drop(columns=["bed_bath_area", "Price"], inplace=True)

        if save:
            if_exists = "replace"
            df.index += 1

            property_types_df = df['Property Type'].drop_duplicates().reset_index().drop('index',
                                                                                         axis=1).reset_index().rename(
                columns={'index': 'Property Type ID'})
            property_types_df.to_sql('property_types_rent', self.conn, if_exists=if_exists, index=False)
            print("property types added to DB with : ", if_exists)

            providers_df = df['provider'].drop_duplicates().reset_index().drop('index', axis=1).reset_index().rename(
                columns={'index': 'Provider ID'})
            providers_df.to_sql('providers_rent', self.conn, if_exists=if_exists, index=False)
            print("providers added to DB with : ", if_exists)

            locations_df = df['Location'].drop_duplicates().reset_index().drop('index', axis=1).reset_index().rename(
                columns={'index': 'Location ID'})
            locations_df.to_sql('locations_rent', self.conn, if_exists=if_exists, index=False)
            print("Locations added to DB with : ", if_exists)

            rent_types_df = df['Rent Type'].drop_duplicates().reset_index().drop('index', axis=1).reset_index().rename(
                columns={'index': 'Rent Type ID'})
            rent_types_df.to_sql('rent_types_rent', self.conn, if_exists=if_exists, index=False)
            print("rent types added to DB with : ", if_exists)

            posting_time_df = df['Posting Time'].drop_duplicates().reset_index().drop('index',
                                                                                      axis=1).reset_index().rename(
                columns={'index': 'Posting Time ID'})
            posting_time_df.to_sql('posting_time_rent', self.conn, if_exists=if_exists, index=False)
            print("posting time added to DB with : ", if_exists)

            # Create the fact table
            fact_df = pd.DataFrame({
                "Property Id": range(1, len(df) + 1),
                "Price": df['price'],
                "Description": df['Description'],
                "Bedrooms": df['bedrooms'],
                "Bathrooms": df['bathrooms'],
                "Area": df['area'],
                "Posting Time": df['Posting Time'],
                "Property Type Id": df['Property Type'].apply(
                    lambda x: property_types_df[property_types_df['Property Type'] == x]['Property Type ID'].values[0]),
                "Provider Id": df['provider'].apply(
                    lambda x: providers_df[providers_df['provider'] == x]['Provider ID'].values[0]),
                "Location Id": df['Location'].apply(
                    lambda x: locations_df[locations_df['Location'] == x]['Location ID'].values[0]),
                "Rent Type Id": df['Rent Type'].apply(
                    lambda x: rent_types_df[rent_types_df['Rent Type'] == x]['Rent Type ID'].values[0]),
                "Posting Time Id": df['Posting Time'].apply(
                    lambda x: posting_time_df[posting_time_df['Posting Time'] == x]['Posting Time'].values[0])
            })

            fact_df.to_sql('facts_rent', self.conn, if_exists=if_exists, index=False)
            print("fact_rent table added in DB with : ", if_exists)

            df.to_sql(name ="rent_df",con=self.conn,if_exists=if_exists, index=False)
            # Close the SQLite connection
            self.conn.close()

        # Close the Chrome driver
        self.driver.quit()



    # ---------------------------------------------- commertial data ---------------------------------------------------

    def collect_com(self,save=True):
        # Extract property data
        property_data = []

        # Iterate over pages
        for i in range(self.pages):

            # Set the target URL
            url = f"https://www.propertyfinder.eg/en/commercial-rent/properties-for-rent.html?page={i + 1}"

            # Load the target URL
            self.driver.get(url)

            # property_elements = driver.find_elements(By.XPATH, "//div[@class='property-card-module_property-card__Yuso0 property-card-module_property-card--DESKTOP__7At5L ']")

            property_elements = self.driver.find_elements(By.XPATH, "//li[contains(@data-testid, 'list-item-')]")
            for property_element in property_elements:
                try:
                    # Extract property type
                    property_type_element = property_element.find_element(By.XPATH,
                                                                          ".//p[@data-testid='property-card-type']")
                    property_type = property_type_element.text.strip()

                    # Extract price
                    price_element = property_element.find_element(By.XPATH, ".//p[@data-testid='property-card-price']")
                    price = price_element.text.strip()

                    # Extract description
                    description_element = property_element.find_element(By.XPATH,
                                                                        ".//h2[@class='styles-module_content__title__eOEkd']")
                    description = description_element.text.strip()

                    # Extract location
                    location_element = property_element.find_element(By.XPATH,
                                                                     ".//div[@data-testid='property-card-location']")
                    location = location_element.text.strip()

                    # Extract number of bedrooms
                    bd_ba_ar_element = property_element.find_element(By.XPATH,
                                                                     ".//div[@data-testid='property-card-details']")
                    bd_ba_ar = bd_ba_ar_element.text.split("\n")

                    # Extract posting time
                    posting_time_element = property_element.find_element(By.XPATH,
                                                                         ".//p[@class='styles-module_footer__publish-info__UVabq']")
                    posting_time = posting_time_element.text.strip()

                    # Extract provider
                    try:
                        provider_container_element = property_element.find_element(By.XPATH,
                                                                                   ".//div[@data-testid='property-card-broker-logo']")
                        provider_element = provider_container_element.find_element(By.XPATH,
                                                                                   ".//img[@data-testid='gallery-picture']")
                        provider = provider_element.get_attribute('title')
                    except:
                        provider = ''

                    # Extract URL
                    url_element = property_element.find_element(By.XPATH,
                                                                ".//a[@class='property-card-module_property-card__link__L6AKb']")
                    url = url_element.get_attribute('href')

                    # Append extracted data to property data list
                    property_data.append({
                        "Property Type": property_type,
                        "Price": price,
                        "Description": description,
                        "Location": location,
                        "bed_bath_area": bd_ba_ar,
                        "Posting Time": posting_time,
                        "provider": provider,
                        "url": url
                    })
                except StaleElementReferenceException:
                    # Handle stale element exceptions due to dynamic page updates
                    pass

        # Create a Pandas DataFrame from the extracted property data
        df = DataFrame(property_data)

        # --------------------------------- wrangle commertial --------------------------------------------------------
        # wrangle rent type
        df["Rent Type"] = df.Price.apply(lambda a: a.replace(",","").split(' ')[-1].replace('EGP/', ''))

        # wrangle price
        df["price"] = df.Price.apply(lambda a: "Ask for price" if a == "Ask for price" else float(a.replace(",","").split(" ")[0]))

        # wrangle bedrooms column
        # df1["bedrooms"] = pd.to_numeric(df1.bed_bath_area.apply(lambda x : x[0] if len(x)==3 else "").str.replace('+', '').replace('studio', '1'),downcast='integer') #bedrooms

        # wrangle bathrooms column
        df["bathrooms"] = pd.to_numeric(
            df.bed_bath_area.apply(lambda x: x[0] if len(x) == 2 else "").str.replace('+', '').replace(",",""),
            downcast='integer')  # bathrooms

        # wrangle area column TODO -------------------------------------------------------
        df["area"] = pd.to_numeric(df.bed_bath_area.apply(
            lambda x: x[1].split(" ")[0].replace("+", "").replace(",", "") if len(x) == 2 else x[-1].split(" ")[0].replace(",","").replace("+", "").replace(",", "")),
                                    downcast='integer')  # area

        # wrangle posting time column
        df['Posting Time'] = df['Posting Time'].str.replace('Listed | ago', '').str.replace("more than ",
                                                                                              "").str.replace("+", "")

        df['Posting Time'] = df['Posting Time'].apply(
            lambda x: subtract_dates_and_time.days_minus(int(x.split(" ")[0]))
            if "days" or "day" in x
            else (subtract_dates_and_time.months_minus(int(x.split(" ")[0]))
                  if "months" or "month" in x
                  else subtract_dates_and_time.hours_minus(int(x.split(" ")[0]))))

        # wrangle provider
        df["provider"] = df.provider.str.replace(' logo image', '')

        # wrangle location column to governorate and city columns
        df["governorate"] = df.Location.apply(lambda x: x.split(",")[-1])

        # wrangle city
        df["city"] = df.Location.apply(lambda x: x.split(",")[-2])

        # drop unnecessary columns
        df.drop(columns=["bed_bath_area", "Price"], inplace=True)

        # --------------------------------------------- save commercial -----------------------------------------------
        if save:
            df.index += 1
            if_exists = "replace"

            property_types_df = df['Property Type'].drop_duplicates().reset_index().drop('index',
                                                                                         axis=1).reset_index().rename(
                columns={'index': 'Property Type ID'})
            property_types_df.to_sql('property_types_com', self.conn, if_exists=if_exists, index=False)
            print("property types added to DB with : ", if_exists)

            providers_df = df['provider'].drop_duplicates().reset_index().drop('index', axis=1).reset_index().rename(
                columns={'index': 'Provider ID'})
            providers_df.to_sql('providers_com', self.conn, if_exists=if_exists, index=False)
            print("providers added to DB with : ", if_exists)

            locations_df = df['Location'].drop_duplicates().reset_index().drop('index', axis=1).reset_index().rename(
                columns={'index': 'Location ID'})
            locations_df.to_sql('locations_com', self.conn, if_exists=if_exists, index=False)
            print("Locations added to DB with : ", if_exists)

            rent_types_df = df['Rent Type'].drop_duplicates().reset_index().drop('index', axis=1).reset_index().rename(
                columns={'index': 'Rent Type ID'})
            rent_types_df.to_sql('rent_types_com', self.conn, if_exists=if_exists, index=False)
            print("rent types added to DB with : ", if_exists)

            posting_time_df = df['Posting Time'].drop_duplicates().reset_index().drop('index', axis=1).reset_index().rename(
                columns={'index': 'Posting Time ID'})
            posting_time_df.to_sql('posting_time_com', self.conn, if_exists=if_exists, index=False)
            print("posting time added to DB with : ", if_exists)

            # Create the fact table
            fact_df = pd.DataFrame({
                "Property Id": range(1, len(df) + 1),
                "Price": df['price'],
                "Description": df['Description'],
                "Bathrooms": df['bathrooms'],
                "Area": df['area'],
                "Posting Time": df['Posting Time'],
                "Property Type Id": df['Property Type'].apply(
                    lambda x: property_types_df[property_types_df['Property Type'] == x]['Property Type ID'].values[0]),
                "Provider Id": df['provider'].apply(
                    lambda x: providers_df[providers_df['provider'] == x]['Provider ID'].values[0]),
                "Location Id": df['Location'].apply(
                    lambda x: locations_df[locations_df['Location'] == x]['Location ID'].values[0]),
                "Rent Type Id": df['Rent Type'].apply(
                    lambda x: rent_types_df[rent_types_df['Rent Type'] == x]['Rent Type ID'].values[0]),
                "Posting Time Id": df['Posting Time'].apply(
                    lambda x: posting_time_df[posting_time_df['Posting Time'] == x]['Posting Time'].values[0])
            })

            fact_df.to_sql('facts_com', self.conn, if_exists=if_exists, index=False)
            print("fact_rent table added in DB with : ", if_exists)

            df.to_sql(name="com_df", con=self.conn,if_exists=if_exists, index=False)

            # Close the SQLite connection
            self.conn.close()
        # Close the Chrome driver
        self.driver.quit()