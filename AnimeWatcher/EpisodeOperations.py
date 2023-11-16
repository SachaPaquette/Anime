class Colors:
    red = '\033[91m'
    green = '\033[92m'
    yellow = '\033[93m'
    endc = '\033[0m'

class EpisodeMenu:

    def __init__(self, start_episode, max_episode):
        self.start_episode = start_episode
        self.max_episode = max_episode
        self.color = Colors()
        
    def reset_cli(self):
        # Clear the screen
        print("\033c", end="")

    def display_menu(self):
        self.reset_cli()
        # print in red color the quit option
        print("\n===== Menu =====\n") 
        print(f"{self.color.green}[N] Next Episode{self.color.endc}\n")
        print(f"{self.color.yellow}[P] Previous Episode{self.color.endc}\n")  
        print(f"{self.color.red}[Q] Quit{self.color.endc}\n")

    def handle_choice(self, user_choice, current_episode):
        if user_choice == 'n':
            return self.next_episode(current_episode)
        elif user_choice == 'p':
            return self.previous_episode(current_episode)
        elif user_choice == 'q':
            return None
        else:
            print("Invalid choice. Please enter 'n', 'p', or 'q'.")
            return current_episode

    def next_episode(self, current_episode):
        if current_episode < self.max_episode:
            return current_episode + 1
        else:
            print("No more episodes available.")
            return current_episode

    def previous_episode(self, current_episode):
        if current_episode > self.start_episode:
            return current_episode - 1
        else:
            print("Already at the first episode.")
            return current_episode
