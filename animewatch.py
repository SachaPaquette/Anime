from AnimeWatcher.WatchOperations import AnimeWatch, Main
from Config.logs_config import setup_logging
from Config.config import Config
from AnimeWatcher.WebOperations import WebInteractions, AnimeInteractions
logger = setup_logging('anime_fetch', Config.MANGA_FETCH_LOG_PATH)

def instantiate_classes():
    """web_interactions = WebInteractions()
    anime_interactions = AnimeInteractions(web_interactions)"""
    
    main = Main()
    return   main
if __name__ == "__main__":
    try:
        
        main = instantiate_classes()
        main.main()
    except Exception as e:
        logger.error(f"Unexpected exception: {e}")
        
        raise  # Re-raise the exception to stop further execution
