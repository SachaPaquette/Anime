# The user will be able to navigate through the animes/episodes and select the one they want to watch.
import curses 
from Config.logs_config import setup_logging
from Config.config import AnimeWatcherConfig
# Setup logging
logger = setup_logging(AnimeWatcherConfig.ANIME_WATCH_LOG_FILENAME,
                       AnimeWatcherConfig.ANIME_WATCH_LOG_PATH)


def displayAnimes(stdscr, anime, cursor):
    try:
        logger.error(f"Allo", anime)
        stdscr.clear()  # Clear the console
        stdscr.addstr(0, 0, f"Select an anime to watch: (1-{len(anime)})\n")

        # Calculate the maximum index to display
        max_index = min(cursor + get_number_of_displays(anime), len(anime))

        # Print the animes within the range
        for i in range(cursor, max_index):
            # Highlight the selected anime
            if i == cursor:
                stdscr.addstr(f"> {anime[i]}\n")
            else:
                # Print the anime
                stdscr.addstr(f"  {anime[i]}\n")
        cursor = max_index
        stdscr.refresh()
        
        
        
    except Exception as e:
        logger.error(f"Error displaying anime list: {e}")
        raise e
    
def get_number_of_displays(anime):
    if len(anime) < 20:
        return len(anime)
    return 20
def displayEpisodes(stdscr, max_episode, cursor):
    try:
        
        stdscr.clear()  # Clear the console
        
        stdscr.addstr(0, 0, f"Select an episode to watch: (1-{len(max_episode)})\n")
    
        # Calculate the maximum index to display
        max_index = min(cursor + get_number_of_displays(max_episode), len(max_episode))
        
        
        # Print the episodes within the range
        for i in range(cursor, max_index):
            # Highlight the selected episode 
            if i == cursor:
                stdscr.addstr(f"> {i + 1}\n")
            else:
                # Print the episode
                stdscr.addstr(f"  {i + 1}\n")
        cursor = max_index
        stdscr.refresh()

    except Exception as e:
        logger.error(f"Error displaying episodes list: {e}")
        raise e

def chose_anime(anime):
    try:
        for i, anime in enumerate(anime):
            print(f"{i + 1}. {anime['title']}")
        return int(input("Enter the index of the anime you want to watch (or 0 to exit): "))
    except Exception as e:
        logger.error(f"Error selecting anime: {e}")
        raise e
    


def animeList(animes):
    try:
        logger.error(f"Allo")
        # Dont use the curses, use the print
        return chose_anime(animes)
    except Exception as e:
        logger.error(f"Error selecting anime: {e}")
        raise e
def episodesList(max_episode):
    try:
            
        list_episodes = []
        for i in range(1, max_episode+1):
            list_episodes.append(i)
        return curses.wrapper(curses_anime_list, list_episodes, displayEpisodes)

    except Exception as e:
        logger.error(f"Error selecting episode: {e}")
        raise e

def curses_anime_list(stdscr, animes, function):
    try:
        
        cursor = 0 
        function(stdscr, animes, cursor)

        while True:
            c = stdscr.getch()

            if c == curses.KEY_UP and cursor > 0:
                cursor -= 1  # Move the cursor up                         
            elif c == curses.KEY_DOWN and cursor < len(animes) - 1:
                cursor += 1  # Move the cursor down               
            elif c == ord('\n'):  # The curses library uses '\n' instead of 'enter'
                return cursor + 1  # Return the selected index
            elif c == ord('q'):
                return 0
            elif c >= ord('0') and c <= ord('9'):
                num_str = chr(c)  # Initialize the string with the first character
                stdscr.addstr(1, 0, f"Entered number: {num_str}")  # Display entered number (for debugging)
                stdscr.refresh()

                stdscr.timeout(700)  # Set input timeout to 700ms

                while True:
                    c = stdscr.getch()  # Get the next character
                    if c >= ord('0') and c <= ord('9'):
                        num_str += chr(c)  # Append the entered number to the string
                        stdscr.addstr(1, 0, f"Entered number: {num_str}")  # Update displayed number (for debugging)
                        stdscr.refresh()
                    else:
                        break  # Exit the loop if the entered character is not a number

                stdscr.timeout(-1)  # Disable timeout after a multi-digit number is entered

                # Update cursor based on the entered number
                if num_str.isdigit():
                    cursor = max(0, min(int(num_str) - 1, len(animes) - 1))

            function(stdscr, animes, cursor)
    except Exception as e:
        logger.error(f"Error in curses anime list: {e}")
        raise e  
            

            
        
        
            
         
