
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from Config.config import WebOperationsConfig, AnimeWatcherConfig, WebElementsConfig
from Config.logs_config import setup_logging
from Driver.driver_config import driver_setup
import re
import requests

logger = setup_logging(AnimeWatcherConfig.ANIME_WATCH_LOG_FILENAME, AnimeWatcherConfig.ANIME_WATCH_LOG_PATH)


class WebInteractions:
    def __init__(self):
        """
        Initializes the WebOperations class.
        """
        self.driver = driver_setup()

    def cleanup(self):
        """Function to close the browser window and quit the driver"""
        self.driver.quit() # Close the browser window
        print("Browser closed")

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

    def find_anime_cards(self, page_number):
        """Function to find the anime cards on the page

        Args:
            page_number (int): The page number

        Returns:
            list: A list of anime cards
        """
        try:
            # Navigate to the anime page
            self.web_interactions.naviguate(
                self.web_interactions.format_anime_url(page_number))

            # Find the anime list body
            anime_list = self.web_interactions.find_single_element(
                By.CLASS_NAME, WebOperationsConfig.ANIME_LIST_BODY)

            if anime_list is None:
                raise Exception("Anime list not found")

            # Find the anime listing
            anime_listing = self.web_interactions.find_single_element(
                By.CSS_SELECTOR, f".{WebOperationsConfig.ANIME_LIST_BODY} > .{WebOperationsConfig.ANIME_LISTING}", element=anime_list)
            if anime_listing is None:
                raise Exception("Anime listing not found")

            # Find the anime cards
            anime_cards = self.web_interactions.find_multiple_elements(
                By.CSS_SELECTOR, f".{WebOperationsConfig.ANIME_LISTING} > {WebElementsConfig.LI_ELEMENT}", element=anime_listing)
            if anime_cards is None:
                raise Exception("Anime cards not found")

            return anime_cards
        except Exception as e:
            logger.error(f"Error while finding anime cards: {e}")
            raise  # Re-raise the exception to stop further execution

    def get_anime_page_data(self, anime_cards):
        """
        Retrieves the anime data from the given anime cards.

        Args:
            anime_cards (list): List of anime cards.

        Returns:
            list: List of dictionaries containing anime data, with each dictionary
                  having 'title' and 'link' keys.

        Raises:
            Exception: If there is an error while getting anime data.
        """
        try:
            anime_data_array = []
            for anime_card in anime_cards:
                # Get the anime title and link
                anime_title = anime_card.find_element(By.XPATH, WebElementsConfig.XPATH_HREF).text
                anime_link = anime_card.find_element(
                    By.XPATH, WebElementsConfig.XPATH_HREF).get_attribute(WebElementsConfig.HREF)
                # Create a dictionary to store the anime data
                anime_data = {
                    'title': anime_title,
                    'link': anime_link
                }
                # Append the anime data to the array
                anime_data_array.append(anime_data)
            # Return the anime data array
            return anime_data_array
        except Exception as e:
            logger.error(f"Error while getting anime data: {e}")
            raise

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
            li_elements = episodes.find_elements(By.CSS_SELECTOR, WebElementsConfig.LI_ELEMENT)
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
            episode_link = li_element.find_element(By.CSS_SELECTOR, WebElementsConfig.HYPERLINK)
            # Find the episode range from the episode link
            ep_start = int(episode_link.get_attribute(WebOperationsConfig.EP_START))
            ep_end = int(episode_link.get_attribute(WebOperationsConfig.EP_END))
            # Return the episode range
            return ep_start, ep_end

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

                    min_start = min(min_start, ep_start)
                    max_end = max(max_end, ep_end)

                return min_start + 1, max_end

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
            url_name = url.split('/')[-1]
            # remove the - between the words 
            # Remove unwanted symbols except hyphen
            # Remove consecutive hyphens (e.g., 'anime--name' becomes 'anime-name')
            url_name = re.sub(r'[\s-]+', '-', re.sub(r'[^a-zA-Z0-9\s-]', '', url_name)).lower()
            # Return the constructed episode url
            return self.construct_episode_link(url_name, prompt)
            
            # Return the formatted anime name
            #self.format_episode_link(url_name, anime_name, prompt)
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
                request = requests.get(url)
                return request.status_code
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
                # Construct the episode link based on the base anime URL and the episode number
                constructed_url = self.format_anime_name_from_url(url, episode_number)

                # Check if the episode link exists (returns 200 if it exists)
                if self.check_url_status(constructed_url) == 200:
                    return constructed_url

                # If the episode link did not exist, try the original and alternative links
                formatted_anime_name = self.format_anime_name(anime_name)
                original_url = self.construct_episode_link(formatted_anime_name, episode_number)

                return self.retry_format_episode_link(original_url, formatted_anime_name, episode_number)

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
            alternative_url = self.construct_episode_link(formatted_anime_name, episode_number)

            if self.check_url_status(alternative_url) == 200:
                self._retry_attempted = True
                return alternative_url

        raise Exception(f"Episode {episode_number} not found")