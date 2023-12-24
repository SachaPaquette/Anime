# Anime CLI Application

## Introduction

This CLI (Command-Line Interface) application allows users to fetch anime data, insert it into a database, and watch episodes directly in the command line.

### Features

    Anime Data Fetching:
        The application fetches anime data from a specified source on the internet.

    Database Integration:
        The fetched anime data is stored in a database for easy retrieval and management.

    Command-Line Episode Viewer:
        Users can select an anime from the database and watch any available episode directly in the command line.

### Dependencies

Before trying to use this application, make sure that your computer contains the applications that follows

- [Python 3.x](https://www.python.org/downloads/)
- [Pip](https://pip.pypa.io/en/stable/installation/)
- [MongoDB Compass](https://www.mongodb.com/try/download/compass)
- [MongoDB Server](https://www.mongodb.com/try/download/community)
- [Chrome Browser](https://www.google.com/chrome/)
- [Mpv](https://mpv.io/)

## Usage

1. **Clone the repository:**

   ```bash
   git clone https://github.com/SachaPaquette/Anime.git
   ```

2. **Navigate to the project directory:**

   ```bash
   cd Anime/
   ```

3. **Install the project's dependencies** <br>
   Windows and Linux:
   ```bash
   python install_dependencies.py
   ```

### Usage


1. **Watching Episodes**

Run the main application to select an anime and watch episodes:

```bash

python animewatch.py
```

Follow the on-screen instructions to navigate and select an anime and episode.

## Roadmap and Future Improvements

- [ ] Add support for more anime sources (9anime, Aniwave, etc.)
- [ ] Make the application more user-friendly (easier naviguation, better instructions, etc.)
- [x] Make the application less reliant on the database (Remove the need to use animefetch.py)
- [ ] Add support for more video players (vlc player, etc.)
- [ ] Make the application easier to use fresh out of the box
- [x] Make a script to install all the dependencies applications on Windows
- [x] Make a script to install all the dependencies applications on Linux
- [ ] Make an anime watched episode tracker

## License

This project is licensed under the MIT - see the LICENSE.md file for details.
