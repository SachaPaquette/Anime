import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    
    
    ##############################
    #        database.py         #
    #        constants           #
    ##############################
    CONNECTION_STRING = os.environ.get("MONGODB_CONNECTION_STRING") # MongoDB connection string
    DATABASE_LOG_PATH = "./Logs/Database.log" # Path to the log file

    ##############################
    #        animewatch.py    #
    #        constants           #
    ##############################
    IMG = 'img'  # Tag name of the image
    DIV = "div"  # Tag name of the div
    SRC = "src"  # Attribute name of the src
    HREF = "href"  # Attribute name of the href
    HYPERLINK = "a"  # Tag name of the hyperlink
    LI_ELEMENT = "li" # Tag name of the list element
    XPATH_HREF = ".//a" # XPath to the hyperlink
    
    ANIME_WATCH_LOG_PATH = "./Logs/AnimeWatch.log" # Path to the log file

    ##############################
    #        animefetch.py       #
    #        constants           #
    ##############################
    GOGO_ANIME_SITE_BASE_URL = "https://gogoanime3.net/anime-list.html?page={}" # Base URL of the GoGoAnime site
    TOTAL_PAGES = 95  # Total number of pages to fetch
    MIN_SLEEP_THRESHOLD = 30 # Sleep after every x pages (to avoid getting blocked by MangaDex)
    MAX_SLEEP_THRESHOLD = 40 # Sleep after every x pages (to avoid getting blocked by MangaDex)
    MIN_SLEEP_DURATION = 60  # Minimum sleep duration in seconds
    MAX_SLEEP_DURATION = 120 # Maximum sleep duration in seconds (randomly chosen between min and max)
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.48",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.254",
    ]  # List of user agents to rotate through
    ANIME_LIST = "film-list" # Class name of the anime list
    ANIME_CARDS = "item" # Class name of the anime cards
    ANIME_FETCH_LOG_PATH = "./Logs/AnimeFetch.log" # Path to the log file
    EXITING_MESSAGE = "Exiting..." # Message to display when exiting the script
    
    ##############################
    #        driver_config.py    #
    ##############################
    
    CRX_PATH = "./Extensions/uBlock-origin.crx" # Path to the AdBlock extension
    EXTENSION_PATH = os.getenv("EXTENSION_PATH") # Path to the AdBlock extension
    
    ##############################
    #        WebOperations.py    #
    ##############################
    
    EP_START = "ep_start" # Start episode number
    EP_END = "ep_end" # End episode number
    EPISODE_PAGE = "episode_page" # Episode page class name
    ANIME_VIDEO_BODY = "anime_video_body" # Anime video body class name
    ANIME_LIST_BODY = "anime_list_body" # Anime list body class name
    ANIME_LISTING = "listing" # Anime listing class name
    QUALITY = "best" # Quality of the video