from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import random
from Config.config import Config
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

"""def driver_setup():
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
   # Set up the driver options
    options = Options()
    # desired_capabilities = caps in the options
    options.add_argument(f'desired_capabilities={caps}')
    
    
    # Keep the browser open after the script finishes executing (for debugging)
    options.add_experimental_option('detach', True)
    # Run in headless mode (without opening a browser window)
    #options.add_argument('--headless')
    # Disable logging (1: INFO, 2: WARNING, 3: ERROR)
    options.add_argument("--log-level=3")
    # Set a random user agent
    options.add_argument(f"user-agent={random.choice(Config.USER_AGENTS)}")

    # add the crx file to the driver so that it can be used
    options.add_extension(Config.CRX_PATH)
    
    # Adding argument to disable the AutomationControlled flag 
    options.add_argument("--disable-blink-features=AutomationControlled")
    # Exclude the collection of enable-automation switches 
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    # Turn-off userAutomationExtension 
    options.add_experimental_option("useAutomationExtension", False) 
    # ChromeDriverManager will install the latest version of ChromeDriver
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)
    # Changing the property of the navigator value for webdriver to undefined 
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    # put the browser in focus
    driver.switch_to.window(driver.current_window_handle)
    return driver"""
    
def driver_setup():
    #options = Options()
    options = uc.ChromeOptions()
    options.add_argument("--log-level=3")
    #options.add_argument("--headless")
    options.headless = False
    options.add_argument(f"user-agent={random.choice(Config.USER_AGENTS)}")
    options.add_extension(Config.CRX_PATH)
    options.add_argument(f'--load-extension={Config.EXTENSION_PATH}')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--no-sandbox')
    # add proxy to the driver
    #options.add_argument(f"--proxy-server={Config.PROXY_LIST}")
    
    driver = uc.Chrome(options=options)
    
    return driver

    

