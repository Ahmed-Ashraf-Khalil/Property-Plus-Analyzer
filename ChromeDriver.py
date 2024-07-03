from selenium import webdriver
import time

def chrome_driver():
    """
    return chrome driver that can pass cloudflare
    """
	
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

    driver = webdriver.Chrome(options=options)

    time.sleep(3)

    return driver