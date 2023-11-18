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

## Usage

1. **Clone the repository:**

    ```bash
    git clone https://github.com/SachaPaquette/Anime.git
    ```

2. **Navigate to the project directory:**

    ```bash
    cd Anime/
    ```

3. **Install the required Python packages:**

    ```bash
    pip install -r Requirements\requirements.txt
    ```



### Usage
Fetching Anime Data

1. **Run the following command to fetch anime data and insert it into the database:**

```bash
python animefetch.py
```

2. **Watching Episodes**

Run the main application to select an anime and watch episodes:

```bash

python animewatch.py
```

Follow the on-screen instructions to navigate and select an anime and episode.

### Dependencies

    - Python 3.x
    - Selenium
    - MongoDB
    - Chrome Browser

## License

This project is licensed under the MIT - see the LICENSE.md file for details.