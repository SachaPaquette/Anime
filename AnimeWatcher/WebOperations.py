import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException, WebDriverException, TimeoutException,  NoSuchWindowException, InvalidSessionIdException
from dotenv import load_dotenv
import time
import requests
from database import find_mangas
from Config.config import Config
import re
import json
import base64
import hashlib
from Config.logs_config import setup_logging
from Driver.driver_config import driver_setup
logger = setup_logging('anime_download', Config.MANGA_DOWNLOAD_LOG_PATH)
class WebInteractions:
    def __init__(self):
        self.driver = driver_setup()

    def cleanup(self):
        """Function to close the browser window and quit the driver"""
        self.driver.quit()
        print("Browser closed")
        
    def naviguate(self, url):
        try:
            self.driver.get(url)
        except Exception as e:
            logger.error(f"Error while navigating to {url}: {e}")
            raise  # Re-raise the exception to stop further execution
        
        
    def find_single_element(self, type_name, value, element=None):
        by_type = getattr(By, type_name.replace(' ', '_').upper())
        if element:
            return element.find_element(by=by_type, value=value)
        else:
            return self.driver.find_element(by=by_type, value=value)
        
            
            
    
    def find_multiple_elements(self, type_name, value, element=None):
            """
            Finds multiple elements on the page using the specified search criteria.

            Args:
                type_name (str): The type of search to perform (e.g., "class name", "tag name", etc.).
                value (str): The value to search for.
                element (WebElement): The element to search within (optional).

            Returns:
                A list of WebElements that match the specified search criteria.
            """
            by_type = getattr(By, type_name.replace(' ', '_').upper())

            if element:
                return element.find_elements(by=by_type, value=value)
            else:
                return self.driver.find_elements(by=by_type, value=value)
            
class AnimeInteractions:           
    def find_anime_cards(self, page_number):
            """Function to find the anime cards on the page

            Args:
                page_number (int): The page number

            Returns:
                list: A list of anime cards
            """
            # Navigate to the anime page
            self.web_interactions.naviguate(self.format_anime_url(page_number))
            # Find the anime cards
            anime_list = self.web_interactions.find_single_element(
                By.CLASS_NAME, Config.ANIME_CARDS)
            anime_cards = self.web_interactions.find_multiple_elements(
                By.CLASS_NAME, Config.ANIME_CARDS, anime_list)
            return anime_cards