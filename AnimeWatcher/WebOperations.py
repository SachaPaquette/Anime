
from selenium.webdriver.common.by import By
from Config.config import WebOperationsConfig, AnimeWatcherConfig, WebElementsConfig
from Config.logs_config import setup_logging
from Driver.driver_config import driver_setup
import re
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Logging configuration
logger = setup_logging(AnimeWatcherConfig.ANIME_WATCH_LOG_FILENAME,
                       AnimeWatcherConfig.ANIME_WATCH_LOG_PATH)


class WebInteractions:
    def __init__(self):
        """
        Initializes the WebOperations class.
        """
        self.driver = driver_setup()
        self.cleanup_done = False



    def cleanup(self):
        try:
            # Check if cleanup has already been performed
            if not self.cleanup_done:
                # Check if the driver is still active
                if self.driver is not None:
                    # Quit the driver
                    self.driver.quit()                    
                    print("\nBrowser closed")
                else:
                    print("No active browser session to close")

                # Set the cleanup flag to True
                self.cleanup_done = True
            else:
                print("Cleanup already performed, skipping.")
        except Exception as e:
            logger.error(f"Error during browser cleanup: {e}")

    def naviguate(self, url):
        """
        Navigates to the specified URL using the Selenium WebDriver.

        Args:
            url (str): The URL to navigate to.

        Raises:
            Exception: If an error occurs while navigating to the URL.

        """
        try:
            # Navigate to the URL
            self.driver.get(url)
        except Exception as e:
            logger.error(f"Error while navigating to {url}: {e}")
            raise  # Re-raise the exception to stop further execution

    def find_single_element(self, type_name, value, element=None):
        """
        Finds a single element on the web page using the specified type and value.

        Args:
            type_name (str): The type of element to search for (e.g., 'id', 'class_name', 'xpath').
            value (str): The value associated with the type of element.
            element (WebElement, optional): The parent element to search within. If not provided, the search will be performed on the entire page.

        Returns:
            WebElement: The found element.

        Raises:
            NoSuchElementException: If the element is not found.
        """
        # Get the search type (e.g., "class name", "tag name", etc.)
        by_type = getattr(By, type_name.replace(' ', '_').upper())
        if element:
            # If an element is provided, search within that element
            return element.find_element(by=by_type, value=value)
        else:
            # If no element is provided, search on the entire page
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
        # Get the search type (e.g., "class name", "tag name", etc.)
        by_type = getattr(By, type_name.replace(' ', '_').upper())
        # If an element is provided, search within that element
        if element:
            # Find the elements within the element provided
            return element.find_elements(by=by_type, value=value)
        else:
            # Find the elements on the entire page
            return self.driver.find_elements(by=by_type, value=value)

    def format_anime_url(self, page_number):
        """Function to format the anime URL with the page number

        Args:
            page_number (int): The page number

        Returns:
            string: The formatted anime URL
        """
        return WebOperationsConfig.GOGO_ANIME_SITE_BASE_URL.format(page_number)

    def exiting_statement(self):
        """Function to print an exiting statement"""
        print(f"\n{WebOperationsConfig.EXITING_MESSAGE}")


class AnimeInteractions:
    def __init__(self, web_interactions):
        """
        Initializes a new instance of the WebOperations class.

        Args:
            web_interactions: The web interactions object used for performing web operations.
        """
        self.web_interactions = web_interactions



    def find_episodes_body(self):
        """
        Finds and returns the episodes body element on the webpage.

        Returns:
            episodes_body (WebElement): The episodes body element.

        Raises:
            Exception: If the episodes list is not found.
        """
        try:
            # Find the episodes body
            episodes_body = self.web_interactions.find_single_element(
                By.CLASS_NAME, WebOperationsConfig.ANIME_VIDEO_BODY)
            if episodes_body is None:
                # If the episodes body is not found, raise an exception
                raise Exception("Episodes list not found")
            # Return the episodes body
            return episodes_body

        except Exception as e:
            logger.error(f"Error while finding episodes body: {e}")
            raise

    def find_episodes(self, episodes_body):
        """
        Finds and returns the episodes element from the given episodes_body.

        Args:
            episodes_body: The body element containing the episodes.

        Returns:
            The episodes element if found.

        Raises:
            Exception: If episodes element is not found.
        """
        try:
            # Find the episodes element
            episodes = self.web_interactions.find_single_element(
                By.ID, WebOperationsConfig.EPISODE_PAGE, element=episodes_body)
            if episodes is None:
                # If the episodes element is not found, raise an exception
                raise Exception("Episodes not found")
            # Return the episodes element
            return episodes

        except Exception as e:
            logger.error(f"Error while finding episodes: {e}")
            raise

    def find_pagination_links(self, pagination_div):
        """Find and return the pagination links from the pagination div.

        Args:
            pagination_div (WebElement): The pagination div element.

        Returns:
            list: A list of pagination links.
        """
        pagination_links = pagination_div.find_elements(
            By.CSS_SELECTOR, WebOperationsConfig.UL_PAGINATION_LIST)
        pages_array = [link.get_attribute('data-page') for link in pagination_links]
        
        # Return the pagination links (i.e., the page numbers)
        return [1] if not pages_array else [link.get_attribute('data-page') for link in pagination_links]
    
    def process_anime_list_page(self, input_anime_name, anime_list, page_number=1):
        """Process a single page of the anime list and return the results.

        Args:
            input_anime_name (str): The input anime name for searching.
            page_number (int): The page number to process.

        Returns:
            list: A list of dictionaries containing anime data.
        """
        
        # Navigate to the anime page
        self.web_interactions.naviguate(
            WebOperationsConfig.GOGO_ANIME_SEARCH.format(input_anime_name) + f"&page={page_number}")

        # Find all the li elements
        li_elements = WebDriverWait(self.web_interactions.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.items'))).find_elements(By.CSS_SELECTOR, WebElementsConfig.LI_ELEMENT)

        # Check if there are any li elements
        if not li_elements:
            raise Exception("Anime list not found")
        
        # Find the first li element
        for li in li_elements:
            # Append the results to the anime list
            anime_list.append({
                'title': li.text.split('\n')[0],
                'link': li.find_element(By.CSS_SELECTOR, WebElementsConfig.HYPERLINK).get_attribute(WebElementsConfig.HREF)
            })
    
    def format_anime_name_from_input(self, input_anime_name):
        try:
            # Format the anime name (replace spaces with %20)
            input_anime_name = input_anime_name.replace(' ', '%20')
            # Return the formatted anime name
            return input_anime_name
        except Exception as e:
            logger.error(f"Error while formatting anime name from input: {e}")
            raise


    def find_anime_website(self, input_anime_name):
        try:
            # Initialize the anime list
            anime_list = []
            
            # Go to the anime website
            self.web_interactions.naviguate(
                WebOperationsConfig.GOGO_ANIME_SEARCH.format(input_anime_name))

            # Check for pagination (multiple pages of results)
            pagination_div = self.web_interactions.find_single_element(
                By.CSS_SELECTOR, WebOperationsConfig.ANIME_NAME_PAGINATION)

            if pagination_div:
                # Find all the pagination links
                page_numbers = self.find_pagination_links(pagination_div)
            
                # Iterate through the page numbers
                for page_number in page_numbers:
                    # Process each page of the anime list
                    self.process_anime_list_page(input_anime_name, anime_list, page_number)
            else:
                # Process the first page if no pagination
                self.process_anime_list_page(input_anime_name, anime_list)
            # Return the anime list
            return anime_list
        except Exception as e:
            logger.error(f"Error while finding anime website: {e}")
            raise


    def find_li_elements(self, episodes):
        """
        Find and return a list of <li> elements within the given 'episodes' element.

        Args:
            episodes (WebElement): The parent element containing the <li> elements.

        Returns:
            list: A list of <li> elements found within the 'episodes' element.

        Raises:
            Exception: If the 'episodes' element is not found or if an error occurs during the process.
        """
        try:
            # Find the <li> elements
            li_elements = episodes.find_elements(
                By.CSS_SELECTOR, WebElementsConfig.LI_ELEMENT)
            if li_elements is None:
                # If no <li> elements are found, raise an exception
                raise Exception("Episodes list not found")
            # Return the <li> elements
            return li_elements

        except Exception as e:
            logger.error(f"Error while finding li elements: {e}")
            raise

    def get_episode_range(self, li_element):
        """
        Get the episode range from the given li_element.

        Args:
            li_element (WebElement): The li element containing the episode information.

        Returns:
            Two variables containing the start and end episode numbers.

        Raises:
            Exception: If there is an error while getting the episode range.
        """
        try:
            # Get the episode link
            episode_link = li_element.find_element(
                By.CSS_SELECTOR, WebElementsConfig.HYPERLINK)    
            # Return the episode range
            return int(episode_link.get_attribute(WebOperationsConfig.EP_START)), int(episode_link.get_attribute(WebOperationsConfig.EP_END))
        except Exception as e:
            logger.error(f"Error while getting episode range: {e}")
            raise

    def get_number_episodes(self):
        """
        Retrieves the number of episodes for the anime.

        Returns:
            Two variables, the minimum and maximum episode numbers.
        Raises:
            Exception: If there is an error while getting the number of episodes.
        """
        try:
            episodes_body = self.find_episodes_body()
            episodes = self.find_episodes(episodes_body)
            li_elements = self.find_li_elements(episodes)

            min_start = float('inf')  # set to positive infinity
            max_end = float('-inf')  # set to negative infinity

            for li_element in li_elements:
                ep_start, ep_end = self.get_episode_range(li_element)
                min_start = 1
                max_end = max(max_end, ep_end)
               
            return min_start, max_end if max_end > 0 else 1

        except Exception as e:
            logger.error(f"Error while getting number of episodes: {e}")
            raise

    def format_anime_name_from_url(self, url, prompt):
        """
        Formats the anime name extracted from the given URL.

        Args:
            url (str): The URL from which the anime name is extracted.

        Returns:
            str: The formatted anime name.

        Raises:
            Exception: If there is an error while formatting the anime name.
        """
        try:
            # split the url by / and get the last part (the url looks like https://gogoanime3.net/anime-name)
            # remove the - between the words
            # Remove unwanted symbols except hyphen
            # Remove consecutive hyphens (e.g., 'anime--name' becomes 'anime-name')  
            # Return the constructed episode url
            return self.construct_episode_link(re.sub(r'[\s-]+', '-', re.sub(r'[^a-zA-Z0-9\s-]', '', url.split('/')[-1])).lower() , prompt)
        except Exception as e:
            logger.error(f"Error while formatting anime name url: {e}")
            raise

    def format_anime_name(self, anime_name):
        """
        Formats the given anime name by removing special characters, converting to lowercase,
        and replacing spaces with hyphens.

        Args:
            anime_name (str): The anime name to be formatted.

        Returns:
            str: The formatted anime name.

        Raises:
            Exception: If an error occurs while formatting the anime name.
        """
        try:
            return re.sub(r'[\s-]+', '-', re.sub(r'[^a-zA-Z0-9\s-]', '', anime_name)).lower()
        except Exception as e:
            logger.error(f"Error while formatting anime name: {e}")
            raise

    def check_url_status(self, url):
        """
        Check the status of a given URL.

        Args:
            url (str): The URL to check.

        Returns:
            int: The status code of the URL.

        Raises:
            Exception: If an error occurs while checking the URL status.
        """
        try:
            return requests.get(url).status_code
        except Exception as e:
            logger.error(f"Error while checking URL status: {e}")
            raise

    def construct_episode_link(self, formatted_anime_name, episode_number):
        """
        Constructs the episode link for a given anime and episode number.

        Args:
            formatted_anime_name (str): The formatted name of the anime.
            episode_number (int): The episode number.

        Returns:
            str: The constructed episode link.
        """
        return f"https://gogoanime3.net/{formatted_anime_name}-episode-{episode_number}"

    def format_episode_link(self, url, anime_name, episode_number):
        """
        Formats the episode link based on the base anime URL and the episode number.

        Args:
            url (str): The base anime URL.
            anime_name (str): The name of the anime.
            episode_number (int): The episode number.

        Returns:
            str: The formatted episode link.

        Raises:
            Exception: If there is an error while formatting the episode link.
        """
        try:
            # Check if the episode link exists (returns 200 if it exists)
            if self.check_url_status(self.format_anime_name_from_url(url, episode_number)) == 200:
                return self.format_anime_name_from_url(url, episode_number)

            # If the episode link did not exist, try the original and alternative links
            return self.retry_format_episode_link(self.construct_episode_link(
                self.format_anime_name(anime_name), episode_number), self.format_anime_name(anime_name), episode_number)
        except Exception as e:
            logger.error(f"Error while formatting episode link: {e}")
            raise

    def retry_format_episode_link(self, original_url, formatted_anime_name, episode_number):
        """
        Retry logic for formatting episode link.

        Args:
            original_url (str): The original URL to check.
            formatted_anime_name (str): The formatted name of the anime.
            episode_number (int): The episode number.

        Returns:
            str: The formatted episode link if successful.

        Raises:
            Exception: If the episode is not found.
        """
        if self.check_url_status(original_url) == 200:
            return original_url

        if not hasattr(self, '_retry_attempted'):
            alternative_url = self.construct_episode_link(
                formatted_anime_name, episode_number)

            if self.check_url_status(alternative_url) == 200:
                self._retry_attempted = True
                return alternative_url

        raise Exception(f"Episode {episode_number} not found")
