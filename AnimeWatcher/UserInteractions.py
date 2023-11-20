class UserInteractions:
    def get_valid_index(self, prompt, max_index):
        """
        Prompts the user for an index and validates it.

        Args:
            prompt (str): The prompt message to display to the user.
            max_index (int): The maximum valid index.

        Returns:
            int: The valid index entered by the user.

        Raises:
            ValueError: If the user enters an invalid number.
        """
        while True:
            try:
                # Prompt the user to enter an index
                selected_index = int(input(prompt))
                # If the user entered a valid index, return it
                if selected_index == 0 or 0 <= selected_index <= max_index:
                    return selected_index  # Return the selected index
                else:
                    print("Invalid index. Please enter a valid index.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def select_anime(self, animes):
        """
        Displays the search results and prompts the user to select an anime.

        Args:
            animes (list): List of anime dictionaries.

        Returns:
            int: The selected index of the anime, or 0 to exit.
        """
        print("Search results: ")
        for i, anime in enumerate(animes):
            # Print the anime's title
            print(f"{i + 1}. {anime['title']}")
        # Prompt the user to enter the index of the anime they want to watch
        return self.get_valid_index("Enter the index of the anime you want to watch (or 0 to exit): ", len(animes))
    
    def get_user_input(self, start_episode, max_episode, web_interactions, logger):
        """
        Prompts the user to enter the episode they want to start watching, between the given start and max episodes.

        Args:
            start_episode (int): The first episode available to watch.
            max_episode (int): The last episode available to watch.

        Returns:
            str: The user's input, which is either a valid episode number or '0' to exit.
        """
        try:
            while True:
                # Prompt the user to enter the episode they want to start watching
                user_input = input(
                    f"Enter the episode you want to start watching between {start_episode}-{max_episode} (or 0 to exit): ")
                # If the user wants to exit, return None to exit the program
                if user_input == '0':
                    web_interactions.exiting_statement()
                    return None
                # If the user entered a valid episode, return the episode number
                if user_input.isdigit() and start_episode <= int(user_input) <= max_episode:
                    return user_input
                # If the user entered an invalid episode, prompt them to enter a valid episode
                else:
                    print("Invalid input. Please enter a valid episode or '0' to exit.")
        except Exception as e:
            # If an error occurs while getting the user's input, log the error and raise it
            logger.error(f"Error while getting user input: {e}")
            raise
        except KeyboardInterrupt:
            # If the user presses Ctrl+C, exit the program
            web_interactions.exiting_statement()
            return None