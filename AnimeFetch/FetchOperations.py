import re
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from database import  detect_duplicates, remove_doujinshi
from tqdm import tqdm  # Import tqdm for the progress bar
import random
from Config.config import Config
from Config.logs_config import setup_logging
from Driver.driver_config import driver_setup
from AnimeWatcher.WebOperations import WebInteractions, AnimeInteractions

logger = setup_logging('anime_fetch', Config.MANGA_FETCH_LOG_PATH)

class AnimeFetch:
    def __init__(self, web_interactions=None, anime_interactions=None):
        self.web_interactions = web_interactions if web_interactions else WebInteractions()
        self.anime_interactions = anime_interactions if anime_interactions else AnimeInteractions()
        
    def format_anime_url(self, page_number):
        """Function to format the anime URL with the page number

        Args:
            page_number (int): The page number

        Returns:
            string: The formatted anime URL
        """
        return Config.ANIME_SITE_BASE_URL.format(page_number)
    
    
    
    def get_user_confirmation(self, prompt, default="y"):
        """
        Prompts the user for confirmation and returns their response.

        Args:
            prompt (str): The prompt to display to the user.
            default (str, optional): The default response if the user enters an empty string. Defaults to "y".

        Returns:
            str: The user's response, either 'y' or 'n'.
        """
        while True:
            # Get user input and convert to lowercase
            user_input = input(f"{prompt} ").lower()
            if user_input in ["y", "n", ""]:  # If the input is 'y', 'n' or empty
                return user_input or default  # Return the input
            else:
                print("Invalid input. Please enter 'y' for yes or 'n' for no.")
                
    def handle_unexpected_exception(self, logger, exception):
        """
        Logs an unexpected exception and re-raises it.

        Args:
            logger: The logger to use for logging the error.
            exception: The exception that was raised.

        Raises:
            The original exception that was passed in.
        """
        logger.error(f"An unexpected error occurred: {exception}")
        raise


    def handle_user_confirmation(self):
        """
        Asks the user for confirmation to add manga names to the database.

        Returns:
            str: The user's input (either 'y' or 'n').
        """
        return self.get_user_confirmation(
        "Do you want to add anime names to the database? (Y/n): ", default="y")
    
    def main(self):
        driver = None  # Initialize the driver variable
        try:
            self.handle_user_confirmation()  # Get user confirmation
            # Set up the driver if needed
            
            # Perform the main workflow (fetching and inserting mangas)
            

        except Exception as e:
            self.handle_unexpected_exception(logger, e)  # Handle unexpected exceptions
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt detected. Quitting...")
        finally:
            self.web_interactions.cleanup()  # Close the browser window