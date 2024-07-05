# Script to watch anime from the command line
from AnimeWatcher.WatchOperations import Main
from Config.logs_config import setup_logging
from Config.config import AnimeWatcherConfig
# Set up the logger
logger = setup_logging(AnimeWatcherConfig.ANIME_WATCH_LOG_FILENAME,AnimeWatcherConfig.ANIME_WATCH_LOG_PATH)

def main():
    try:
        Main().main()
    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        logger.error(f"Unexpected exception in animewatch.py: {e}")
        raise   
if __name__ == "__main__":
    main()
        
