from AnimeFetch.FetchOperations import AnimeFetch
from Config.logs_config import setup_logging
from Config.config import Config

logger = setup_logging('anime_fetch', Config.MANGA_FETCH_LOG_PATH)

if __name__ == "__main__":
    try:
        anime_fetch = AnimeFetch()
        anime_fetch.main()
    except Exception as e:
        logger.error(f"Unexpected exception: {e}")
        raise  # Re-raise the exception to stop further execution