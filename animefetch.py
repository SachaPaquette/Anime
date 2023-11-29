from AnimeFetch.FetchOperations import AnimeFetch
from Config.logs_config import setup_logging
from Config.config import AnimeFetcherConfig
from AnimeWatcher.WebOperations import WebInteractions, AnimeInteractions

# Set up the logger
logger = setup_logging('anime_fetch', AnimeFetcherConfig.ANIME_FETCH_LOG_PATH)

if __name__ == "__main__":
    try:
        web_interactions = WebInteractions() # Instantiate the WebInteractions class
        anime_interactions = AnimeInteractions(web_interactions) 
        anime_fetch = AnimeFetch(web_interactions, anime_interactions) 
        anime_fetch.main() # Call the main method
    except Exception as e:
        logger.error(f"Unexpected exception: {e}")
        raise  # Re-raise the exception to stop further execution