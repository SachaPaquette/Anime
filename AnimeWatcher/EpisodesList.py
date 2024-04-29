# The user will be able to navigate through the animes/episodes and select the one they want to watch.
import curses 
def displayAnimes(stdscr, anime, cursor):
    
    stdscr.clear()  # Clear the console
    
    
    
    stdscr.addstr(0, 0, f"Select an anime to watch: (1-{len(anime)})\n")
    
    for i, ani in enumerate(anime):
        if i == cursor:
            stdscr.addstr(f"> {i + 1}. {ani['title']}\n")  # Highlight the selected episode
        else:
            # print the next 20 episodes after the cursor
            if i > cursor and i < cursor + 20:
                stdscr.addstr(f"  {i + 1}. {ani['title']}\n")  # Print the episode

    stdscr.refresh()
    
def get_number_of_displays(anime):
    if len(anime) < 20:
        return len(anime)
    return 20
def displayEpisodes(stdscr, max_episode, cursor):
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

    

def animeList(animes):
    
    return curses.wrapper(curses_anime_list, animes, displayAnimes)
    
def episodesList(max_episode):
    
    list_episodes = []
    for i in range(1, max_episode+1):
        list_episodes.append(i)
    return curses.wrapper(curses_anime_list, list_episodes, displayEpisodes)


def curses_anime_list(stdscr, animes, function):
    cursor = 0 
    function(stdscr, animes, cursor)

    while True:
        c = stdscr.getch()

        if c == curses.KEY_UP and cursor > 0:
            cursor -= 1                                             # Move the cursor up                         
        elif c == curses.KEY_DOWN and cursor < len(animes) - 1:
            cursor += 1                                             # Move the cursor down               
        elif c == ord('\n'):                                        # The curses library uses '\n' instead of 'enter'
            
            return cursor+1                                         # Return the selected index
        elif c == ord('q'):
            return 0
        
        elif c >= ord('0') and c <= ord('9'):
            num_str = chr(c)  # Initialize the string with the first character
            cursor = int(num_str) - 1  # Update cursor immediately
            function(stdscr, animes, cursor)  # Update the display

            timeout = 700  # Set timeout (in milliseconds) to wait for additional digits
            stdscr.timeout(timeout)  # Set input timeout

            while True:
                c = stdscr.getch()  # Get the next character
                if c >= ord('0') and c <= ord('9'):
                    num_str += chr(c)  # Append the entered number to the string
                    cursor = max(0, min(int(num_str) - 1, len(animes) - 1))  # Update the cursor
                    function(stdscr, animes, cursor)  # Update the display
                else:
                    stdscr.timeout(-1)  # Disable timeout after a multi-digit number is entered
                    break  # Exit the loop if the entered character is not a number

            function(stdscr, animes, cursor)


        function(stdscr, animes, cursor)
        
        

        
        
        
            
         
