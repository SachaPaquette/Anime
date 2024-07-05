# The user will be able to naviguate through the animes/episodes and select the one they want to watch.
import curses 
from Config.logs_config import setup_logging
from Config.config import AnimeWatcherConfig
from AnimeWatcher.TrackerOperations import EpisodeTracker
# Setup logging
logger = setup_logging(AnimeWatcherConfig.ANIME_WATCH_LOG_FILENAME,AnimeWatcherConfig.ANIME_WATCH_LOG_PATH)

def displayAnimes(stdscr, anime, cursor):
    try:
        stdscr.clear()  # Clear the console
        stdscr.addstr(0, 0, f"Select an anime to watch: (1-{len(anime)})\n")

        # Get screen dimensions
        height, width = stdscr.getmaxyx()

        # Calculate the range of episodes to display
        display_range = min(20, height - 2)  # Ensure we don't try to display more lines than the screen can fit
        start = max(0, cursor - display_range // 2)
        end = min(start + display_range, len(anime))
        if end - start < display_range:  # Adjust start if end is at the end of the list
            start = max(0, end - display_range)
        for i in range(start, end):
            ani = anime[i]
            line = f"> {i + 1}. {ani['title']}\n" if i == cursor else f"  {i + 1}. {ani['title']}\n"
            if len(line) > width:
                line = line[:width - 1]  # Truncate the line if it's too long
            try:
                stdscr.addstr(i - start + 1, 0, line, curses.A_REVERSE if i == cursor else 0)  # Highlight the selected episode
            except curses.error:
                logger.error(f"Error displaying anime list: {line}")
                raise Exception("Error displaying anime list")
        stdscr.refresh()
    except Exception as e:
        logger.error(f"Error displaying anime list: {e}")
        raise e

    
def get_number_of_displays(anime):
    if len(anime) < 20:
        return len(anime)
    return 20

def setup_colors():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    
def displayEpisodes(stdscr, episodes, cursor):
    try:
        setup_colors()  # Setup colors for red and green
        stdscr.clear()  # Clear the console
        
        stdscr.addstr(0, 0, f"Select an episode to watch: (1-{len(episodes)})\n")
    
        # Calculate the maximum index to display
        display_range = 20
        start = max(0, cursor - display_range // 2)
        end = min(start + display_range, len(episodes))

        if (end - start) < display_range:  # Adjust start if end is at the end of the list
            start = max(0, end - display_range)

        # Print the episodes within the range
        for i in range(start, end):
            if (i == cursor):
                color_pair = curses.color_pair(1) | curses.A_REVERSE  if episodes[i]['watched'] else curses.color_pair(2) | curses.A_REVERSE
            else:
                color_pair = curses.color_pair(1) if episodes[i]['watched'] else curses.color_pair(2)
            
            stdscr.addstr(f"{'> ' if (i == cursor) else '  '}{episodes[i]['episode']}\n", color_pair)

        stdscr.refresh()

    except Exception as e:
        logger.error(f"Error displaying episodes list: {e}")
        raise e

def animeList(animes):
    try:
        return curses.wrapper(curses_anime_list, animes, displayAnimes)
    except Exception as e:
        logger.error(f"Error selecting anime: {e}")
        raise e
def episodesList(max_episode, watched_list):
    try:        
        return curses.wrapper(curses_anime_list, [{'episode': i, 'watched': i in watched_list} for i in range(1, max_episode + 1)], displayEpisodes)
    except Exception as e:
        logger.error(f"Error selecting episode: {e}")
        raise e

def curses_anime_list(stdscr, animes, function):
    try:
        cursor = 0 
        function(stdscr, animes, cursor)
        
        while True:
            c = stdscr.getch()
            # Check for arrow key input
            if c == curses.KEY_UP and cursor > 0:
                cursor -= 1  # Move the cursor up                         
            elif c == curses.KEY_DOWN and cursor < len(animes) - 1:
                cursor += 1  # Move the cursor down
            elif c == ord('\n'):  # The curses library uses '\n' instead of 'enter'
                return cursor + 1  # Return the selected index
            elif c == ord('q'):
                return 0
            elif ord('0') <= c <= ord('9'):
                num_str = handle_number_input(stdscr, c)
                cursor = update_cursor(num_str, len(animes))
            
            function(stdscr, animes, cursor)
    
    except Exception as e:
        logger.error(f"Error in curses anime list: {e}")
        raise e


def handle_number_input(stdscr, initial_char):
    num_str = chr(initial_char)  # Initialize the string with the first character
    display_number_input(stdscr, num_str)
    
    stdscr.timeout(700)  # Set input timeout to 700ms
    while True:
        c = stdscr.getch()  # Get the next character
        if ord('0') <= c <= ord('9'):
            num_str += chr(c)  # Append the entered number to the string
            display_number_input(stdscr, num_str)
        else:
            break  # Exit the loop if the entered character is not a number
    
    stdscr.timeout(-1)  # Disable timeout after a multi-digit number is entered
    return num_str


def display_number_input(stdscr, num_str):
    stdscr.addstr(stdscr.getmaxyx()[0] - 1, 0, f"Entered number: {num_str}")  # Display entered number at the bottom
    stdscr.clrtoeol()  # Clear to the end of line to handle shorter inputs overwriting longer ones
    stdscr.refresh()


def update_cursor(num_str, max_length):
    if num_str.isdigit():
        return max(0, min(int(num_str) - 1, max_length - 1))
    return 0

            

            
        
        
            
         
