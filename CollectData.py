from pandas import DataFrame
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException

class CollectData:
    def __init__ (self,driver,pages_number):
        self.driver = driver
        self.pages_number = pages_number

    def get_data(self,category="buy"):

        """
        get the data 
        category - buy : properties for sale
                 - rent : properties for rent
                 - commertial : commertial properties
        """
        
        property_data = []
        
        if category == "buy":
            url = "https://www.propertyfinder.eg/en/buy/properties-for-sale.html?page="
                
        elif category == "rent":
            url = "https://www.propertyfinder.eg/en/search?c=2&fu=0&rp=m&ob=mr&page="


        elif category == "commertial":
            url = "https://www.propertyfinder.eg/en/commercial-rent/properties-for-rent.html?page="

        else:
            print("please chose weither : buy - rent - commertial")
            
        
        pages= [f"{url}{i+1}" for i in range(self.pages_number)]
        
        for page in pages:
            self.driver.get(page)            

            property_elements = self.driver.find_elements(By.XPATH, "//li[contains(@data-testid, 'list-item-')]")
            for property_element in property_elements:
                try:
                    property_type_element = property_element.find_element(By.XPATH, ".//p[@data-testid='property-card-type']")
                    property_type = property_type_element.text.strip()

                    price_element = property_element.find_element(By.XPATH, ".//p[@data-testid='property-card-price']")
                    price = price_element.text.strip()

                    description_element = property_element.find_element(By.XPATH, ".//h2[@class='styles-module_content__title__eOEkd']")
                    description = description_element.text.strip()

                    location_element = property_element.find_element(By.XPATH, ".//div[@data-testid='property-card-location']")
                    location = location_element.text.strip()

                    bed_bath_area_element = property_element.find_element(By.XPATH, ".//div[@data-testid='property-card-details']")
                    bed_bath_area = bed_bath_area_element.text.split("\n")

                    posting_time_element = property_element.find_element(By.XPATH, ".//p[@class='styles-module_footer__publish-info__UVabq']")
                    posting_time = posting_time_element.text.strip()

                    try:
                        provider_container_element = property_element.find_element(By.XPATH, ".//div[@data-testid='property-card-broker-logo']")
                        provider_element = provider_container_element.find_element(By.XPATH, ".//img[@data-testid='gallery-picture']")
                        provider = provider_element.get_attribute('title')

                    except:
                        provider = ''

                    url_element = property_element.find_element(By.XPATH, ".//a[@class='property-card-module_property-card__link__L6AKb']")
                    url = url_element.get_attribute('href')

                    property_data.append({
                        "Property Type": property_type,
                        "Price": price,
                        "Description": description,
                        "Location": location,
                        "bed_bath_area": bed_bath_area,
                        "Posting Time": posting_time,
                        "provider": provider,
                        "url": url
                    })

                except StaleElementReferenceException:
                    pass

        data_frame = DataFrame(property_data)
        return data_frame

   

