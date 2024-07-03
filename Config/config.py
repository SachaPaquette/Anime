import os
from dotenv import load_dotenv
load_dotenv()

class DatabaseConfig:
    
    ##############################
    #        Database            #
    ##############################

    CONNECTION_STRING = os.environ.get("MONGODB_CONNECTION_STRING")
    DATABASE_LOG_PATH = "./Logs/Database.log"
class AnimeWatcherConfig:
    ##############################
    #        Anime Watch          #
    ##############################


    ANIME_WATCH_LOG_PATH = "./Logs/AnimeWatch.log"
    ANIME_WATCH_LOG_FILENAME = "AnimeWatch"

class AnimeFetcherConfig:
    ##############################
    #        Anime Fetch          #
    ##############################
    ANIME_FETCH_LOG_PATH = "./Logs/AnimeFetch.log"
    ANIME_FETCH_LOG_FILENAME = "AnimeFetch"
    TOTAL_PAGES = 95
    MIN_SLEEP_THRESHOLD = 30
    MAX_SLEEP_THRESHOLD = 40
    MIN_SLEEP_DURATION = 60
    MAX_SLEEP_DURATION = 120
    
    

class DriverConfig:
    ##############################
    #        Driver Config        #
    ##############################

    CRX_PATH = "Extensions/uBlock-Origin.crx"
    EXTENSION_PATH = os.getenv("EXTENSION_PATH")
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.48",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.254",
    ]
class WebOperationsConfig:
    ##############################
    #        Web Operations       #
    ##############################
    GOGO_ANIME_SITE_BASE_URL = "https://gogoanime3.net/anime-list.html?page={}"
    GOGO_ANIME_SEARCH = "https://gogoanime3.net/search.html?keyword={}"
    EXITING_MESSAGE = "Exiting..."
    EP_START = "ep_start"
    EP_END = "ep_end"
    EPISODE_PAGE = "episode_page"
    ANIME_VIDEO_BODY = "anime_video_body"
    ANIME_LIST_BODY = "anime_list_body"
    ANIME_LISTING = "listing"
    ANIME_LIST = "film-list"
    ANIME_CARDS = "item"
    QUALITY = "best"
    ANIME_NAME_PAGINATION = "div.anime_name_pagination"
    UL_PAGINATION_LIST = "ul.pagination-list li a"
    
class WebElementsConfig:
    
    IMG = 'img'  # Tag name of the image
    DIV = "div"  # Tag name of the div
    SRC = "src"  # Attribute name of the src
    HREF = "href"  # Attribute name of the href
    HYPERLINK = "a"  # Tag name of the hyperlink
    LI_ELEMENT = "li"  # Tag name of the list element
    XPATH_HREF = ".//a"  # XPath to the hyperlink
    
class ScriptConfig:
    windows_script = "./Scripts/windowsinstaller.ps1"
    linux_script = "./Scripts/linuxinstaller.sh"
    requirements_file = "./Requirements/requirements.txt"
    SCRIPT_FILENAME = "installer"
    SCRIPT_LOG_PATH = "./Logs/Installer.log"
    windows_curse = "windows-curses"
    venv_name = "AnimeWatcherEnv"
    
class EpisodeTrackerConfig:
    ##############################
    #        Episode Tracker      #
    ##############################
    ANIME_WATCHER_JSON_FILE = "./AnimeWatcher/EpisodeTracker/episode_tracker.json"
    EPISODE_TRACKER_LOG_PATH = "./Logs/EpisodeTracker.log"
    EPISODE_TRACKER_LOG_FILENAME = "EpisodeTracker"