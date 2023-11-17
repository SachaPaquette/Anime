
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from Config.config import Config
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
                print("Element found")
                return element.find_elements(by=by_type, value=value)
            else:
                return self.driver.find_elements(by=by_type, value=value)
    
    def click_on_element(self, element):
        """Function to click on an element

        Args:
            element (WebElement): The element to click on
        """
        try:
            element.click()
        except ElementClickInterceptedException:
            # Scroll to the element
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            # Click on the element again
            element.click()
        except Exception as e:
            logger.error(f"Error while clicking on element: {e}")
            raise  # Re-raise the exception to stop further execution
        
    
    
    
    def format_anime_url(self, page_number):
        """Function to format the anime URL with the page number

        Args:
            page_number (int): The page number

        Returns:
            string: The formatted anime URL
        """
        return Config.GOGO_ANIME_SITE_BASE_URL.format(page_number)     
       
class AnimeInteractions:
    def __init__(self, web_interactions):
        self.web_interactions = web_interactions
                  
    def find_anime_cards(self, page_number):
        """Function to find the anime cards on the page

        Args:
            page_number (int): The page number

        Returns:
            list: A list of anime cards
        """
        try:
            # Navigate to the anime page
            self.web_interactions.naviguate(self.web_interactions.format_anime_url(page_number))

            # Find the anime list body
            anime_list = self.web_interactions.find_single_element(
                By.CLASS_NAME, "anime_list_body")

            if anime_list is None:
                raise Exception("Anime list not found")

            # Find the anime listing
            anime_listing = self.web_interactions.find_single_element(
                By.CSS_SELECTOR, ".anime_list_body > .listing", element=anime_list)
            if anime_listing is None:
                raise Exception("Anime listing not found")

            # Find the anime cards
            anime_cards = self.web_interactions.find_multiple_elements(
                By.CSS_SELECTOR, ".listing > li", element=anime_listing)
            if anime_cards is None:
                raise Exception("Anime cards not found")

            return anime_cards
        except Exception as e:
            logger.error(f"Error while finding anime cards: {e}")
            raise  # Re-raise the exception to stop further execution

            
        
    def get_anime_page_data(self, anime_cards):
        try:
            anime_data_array = []
            for anime_card in anime_cards:
                anime_title = anime_card.find_element(By.XPATH, './/a').text
                anime_link = anime_card.find_element(By.XPATH, './/a').get_attribute('href')
                anime_data = {
                    'title': anime_title,
                    'link': anime_link
                }

                anime_data_array.append(anime_data)
            return anime_data_array
        except Exception as e:
            logger.error(f"Error while getting anime data: {e}")
            raise
    
    #TODO: Format this function to be cleaner, create more functions to make it more readable        
    def get_number_episodes(self):
        try:
            episodes_body = self.web_interactions.find_single_element(By.CLASS_NAME, 'anime_video_body')
            if episodes_body is None:
                raise Exception("Episodes list not found")
            
            episodes = self.web_interactions.find_single_element(By.ID, 'episode_page', element=episodes_body)
            if episodes is None:
                raise Exception("Episodes not found")
            
            # Find all <li> elements
            li_elements = episodes.find_elements(By.CSS_SELECTOR, 'li')
            if li_elements is None:
                raise Exception("Episodes list not found")
            
            # Initialize variables to track min and max values
            min_start = float('inf')  # set to positive infinity
            max_end = float('-inf')  # set to negative infinity

            for li_element in li_elements:
                episode_link = li_element.find_element(By.CSS_SELECTOR, 'a')
                ep_start = int(episode_link.get_attribute('ep_start'))
                ep_end = int(episode_link.get_attribute('ep_end'))

                # Update min and max values
                min_start = min(min_start, ep_start)
                max_end = max(max_end, ep_end)

            
            return min_start + 1, max_end

        except Exception as e:
            logger.error(f"Error while getting number of episodes: {e}")
            raise

    def format_anime_name(self, anime_name):
        """
        Formats the given anime name by replacing spaces with hyphens and converting it to lowercase.

        Args:
            anime_name (str): The name of the anime to be formatted.

        Returns:
            str: The formatted anime name.

        Raises:
            Exception: If there is an error while formatting the anime name.
        """
        try:
            anime_name = anime_name.replace(' ', '-').lower()
            return anime_name
        except Exception as e:
            logger.error(f"Error while formatting anime name url: {e}")
            raise

    def format_episode_link(self, episode_number, anime_name):
        """
        Formats the episode link for a given episode number and anime name.

        Args:
            episode_number (int): The episode number.
            anime_name (str): The name of the anime.

        Returns:
            str: The formatted episode link.

        Raises:
            Exception: If there is an error while formatting the episode link.
        """
        try:
            url = f"https://gogoanime3.net/{anime_name}-episode-{episode_number}"
            return url
        except Exception as e:
            logger.error(f"Error while formatting episode link: {e}")
            raise

