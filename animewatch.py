from AnimeWatcher.WatchOperations import Main
from Config.logs_config import setup_logging
from Config.config import Config
from AnimeWatcher.WebOperations import WebInteractions, AnimeInteractions
logger = setup_logging('anime_watch', Config.ANIME_WATCH_LOG_PATH)

def instantiate_classes():
    main = Main()
    return   main
if __name__ == "__main__":
    try:
        main = Main() # Instantiate the class
        main.main()
    except Exception as e:
        logger.error(f"Unexpected exception: {e}")
        
        raise  # Re-raise the exception to stop further execution
