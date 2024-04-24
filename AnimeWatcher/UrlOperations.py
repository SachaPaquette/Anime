from Config.logs_config import setup_logging
from Config.config import AnimeWatcherConfig
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter, Retry
from Cryptodome.Cipher import AES
from urllib.parse import urlparse, parse_qsl, urlencode
import re
import base64
import json

# Setup logging
logger = setup_logging(AnimeWatcherConfig.ANIME_WATCH_LOG_FILENAME,
                       AnimeWatcherConfig.ANIME_WATCH_LOG_PATH)


class UrlInteractions:

    def __init__(self, quality=None):
        """
        Initializes a new instance of the UrlOperations class.

        Args:
            quality (str): The quality of the video.

        Returns:
            None
        """
        # Create a new session
        self.session = requests.Session()
        # retry the request 3 times with a backoff factor of 0.5 (backoff factor = 0.5 means that the retry will sleep for 0.5 seconds before retrying)
        retry = Retry(connect=3, backoff_factor=0.5)
        # create a new HTTP adapter
        adapter = HTTPAdapter(max_retries=retry)
        # mount the HTTP adapter to the session
        self.session.mount("http://", adapter)
        # mount the HTTPS adapter to the session
        self.session.mount("https://", adapter)
        # the URL to the AJAX endpoint (used for decrypting the video URL)
        self.ajax_url = "/encrypt-ajax.php?"
        # the mode to use for AES encryption
        self.mode = AES.MODE_CBC
        # the padding function to use for AES encryption
        self.padding = lambda s: s + chr(len(s) % 16) * (16 - len(s) % 16)

    def close_session(self):
        """Closes the session."""
        self.session.close()

    def check_response_error(self, request, url):
        """
        Raises an exception if the request to the given URL is not successful.

        Args:
            request (requests.Response): The response object returned by the request.
            url (str): The URL that was requested.

        Raises:
            Exception: If the request was not successful, an exception is raised with an error message.
        """
        # Check if the request was successful
        if request.ok:
            pass
        else:
            # If the request was not successful, raise an exception with an error message
            logger.error(
                f"Error while requesting {url}: {request.status_code}")
            raise Exception(
                f"Error while requesting {url}: {request.status_code}")

    def locating_element_error(self, soup, link, element):
        """
        Raises an exception if the specified element cannot be located in the given link's HTML soup.

        Args:
            soup: The HTML soup of the link.
            link: The URL of the link.
            element: The element to locate in the HTML soup.

        Raises:
            Exception: If the specified element cannot be located in the HTML soup.
        """
        # Check if the element exists
        if soup == None:
            logger.error(f"Error while locating {element} in {link}")
            raise Exception(f"Error while locating {element} in {link}")

    def get_soup_object(self, url):
        """
        Retrieves the HTML soup of the given URL.

        Args:
            url (str): The URL to retrieve the HTML soup for.

        Returns:
            BeautifulSoup: The HTML soup of the given URL.
        """
        try:
            # Send a GET request to the URL
            request = self.session.get(url)
            # Check if the request was successful
            self.check_response_error(request, url)
            # Create a BeautifulSoup object from the response content
            soup = BeautifulSoup(request.content, "html.parser")
            # Return the BeautifulSoup object
            return soup
        except Exception as e:
            raise Exception(f"Error while getting HTML soup: {e}")

    def create_embedded_url(self, active_link):
        """
        Creates an embedded URL from the given active link.

        Args:
            active_link (bs4.element.Tag): The active link.

        Returns:
            str: The embedded URL.
        """
        # Get the embedded video player URL
        embedded_url = f'https:{active_link["data-video"]}' if not active_link["data-video"].startswith(
            "https:") else active_link["data-video"]
        # Return the embedded video player URL
        return embedded_url

    def get_embedded_video_url(self, episode_url):
        """
        Given an episode URL, returns the URL of the embedded video player for that episode.

        Args:
        - episode_url (str): The URL of the episode to get the embedded video player URL for.

        Returns:
        - str: The URL of the embedded video player for the given episode.

        Raises:
        - Exception: If there is an error while getting the embedded video player URL.
        """
        try:
            # Get the HTML soup of the episode URL
            soup = self.get_soup_object(episode_url)

            # Find the active link
            active_link = soup.find("a", {"class": "active", "rel": "1"})
            # Check if the active link exists
            self.locating_element_error(active_link, episode_url, "embed-url")

            # Get the embedded video player URL
            embedded_url = self.create_embedded_url(active_link)
            # Return the embedded video player URL
            return embedded_url
        except Exception as e:
            # Add more details to the error message if needed
            raise Exception(
                f"Error while getting embedded video player URL: {e}")

    def get_data(self, ep_url):
        """
        Retrieves the data for a given episode URL.

        Args:
            ep_url (str): The URL of the episode to retrieve data for.

        Returns:
            str: The data for the given episode URL.
        """
        try:
            # Get the HTML soup of the episode URL
            soup = self.get_soup_object(ep_url)
            # Find the script tag containing the data
            crypto = soup.find("script", {"data-name": "episode"})
            # Check if the requested data exists
            self.locating_element_error(crypto, ep_url, "token")
            # Return the data
            return crypto["data-value"]
        except Exception as e:
            raise Exception(f"Error while getting data: {e}")

    def get_encryption_key(self, ep_url):
        """
        Retrieves the encryption key for the given episode URL.

        Args:
            ep_url (str): The URL of the episode to retrieve the encryption key for.

        Returns:
            dict: A dictionary containing the encryption key, initialization vector, and second key.
        """
        try:
            # Send a GET request to the episode URL
            page = self.session.get(ep_url).text
            # Find the encryption keys
            keys = re.findall(r"(?:container|videocontent)-(\d+)", page)
            # Check if there are any keys found
            if not keys or len(keys) != 3:
                raise ValueError("No encryption keys were found.")
            # Create variables for the encryption keys and initialization vector (IV) from the list of keys
            key, iv, second_key = keys
            # Return the encryption keys as a dictionary
            return {
                "key": key.encode(),
                "iv": iv.encode(),
                "second_key": second_key.encode()
            }
        except Exception as e:
            raise Exception(f"Error while getting encryption key: {e}")

    def aes_encrypt(self, data, key, iv):
        """
        Encrypts the given data using AES encryption with the specified key and initialization vector (IV).

        Args:
            data (str): The data to be encrypted.
            key (bytes): The encryption key.
            iv (bytes): The initialization vector.

        Returns:
            bytes: The encrypted data in base64-encoded format.
        """
        return base64.b64encode(
            AES.new(key, self.mode, iv=iv).encrypt(self.padding(data).encode())
        )

    def aes_decrypt(self, data, key, iv):
        """
        Decrypts the given data using AES encryption with the specified key and initialization vector (IV).

        Args:
            data (bytes): The encrypted data to decrypt.
            key (bytes): The key to use for decryption.
            iv (bytes): The initialization vector to use for decryption.

        Returns:
            bytes: The decrypted data.
        """
        try:
            return (
                AES.new(key, self.mode, iv=iv)
                .decrypt(base64.b64decode(data))
                .strip(b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10")
            )
        except Exception as e:
            raise Exception(f"Error during AES decryption of data: {e}")

    def create_ajax_url(self, ep_url):
        """
        Creates an AJAX URL for the given episode URL.

        Args:
            ep_url (str): The URL of the episode.

        Returns:
            str: The AJAX URL for the given episode URL.
        """
        parsed_url = urlparse(ep_url)  # parse the url
        return parsed_url.scheme + "://" + parsed_url.netloc + self.ajax_url

    def decrypt_url(self, ep_url, encryption_keys):
        """
        Decrypts the given episode URL using the provided encryption keys.

        Args:
            ep_url (str): The URL of the episode to decrypt.
            encryption_keys (dict): A dictionary containing the encryption key and initialization vector.

        Returns:
            str: The decrypted episode URL.
        """
        return self.aes_decrypt(self.get_data(ep_url), encryption_keys["key"], encryption_keys["iv"]).decode()

    def create_dict_data(self, ep_url, encryption_keys, encrypted_id):
        """
        Creates a dictionary of data for a given episode URL, encryption keys, and encrypted ID.

        Args:
            ep_url (str): The URL of the episode.
            encryption_keys (list): A list of encryption keys.
            encrypted_id (str): The encrypted ID of the episode.

        Returns:
            dict: A dictionary of data for the given episode.
        """
        # decrypt the url
        data = self.decrypt_url(ep_url, encryption_keys)
        # parse the data
        data = dict(parse_qsl(data))
        # update the id
        data.update(id=encrypted_id)
        # return the data
        return data

    def encrypt_id(self, id, encryption_keys):
        """
        Encrypts the given ID using AES encryption.

        Args:
            id (str): The ID to encrypt.
            encryption_keys (dict): A dictionary containing the encryption key and initialization vector.

        Returns:
            str: The encrypted ID.
        """
        return self.aes_encrypt(id, encryption_keys["key"], encryption_keys["iv"]).decode()

    def create_id(self, ep_url):
        """
        Extracts the 'id' parameter from the query string of the given episode URL.

        Args:
            ep_url (str): The URL of the episode.

        Returns:
            str: The value of the 'id' parameter in the query string.
        """
        id = urlparse(ep_url).query
        return dict(parse_qsl(id))["id"]

    def create_headers(self, ep_url):
        """
        Creates headers for HTTP requests.

        Args:
            ep_url (str): The URL of the episode.

        Returns:
            dict: A dictionary containing the headers.
        """
        return {
            "x-requested-with": "XMLHttpRequest",
            "referer": ep_url,
        }

    def send_post_request(self, url, data, id, header):
        """
        Sends a POST request to the specified URL with the given data and headers.

        Args:
            url (str): The URL to send the request to.
            data (dict): The data to include in the request.
            id (str): The alias to include in the request.
            header (dict): The headers to include in the request.

        Returns:
            The response from the server.
        """
        try:
            return self.session.post(url + urlencode(data) + f"&alias={id}", headers=header)
        except requests.RequestException as e:
            raise Exception(f"Error while sending POST request: {e}")

    def create_json_response(self, request, encryption_keys):
        """
        Decrypts the data in the request using the provided encryption keys and returns the resulting JSON object.

        Args:
            request (Request): The request object containing the encrypted data.
            encryption_keys (dict): A dictionary containing the encryption keys and initialization vector.

        Returns:
            dict: The decrypted JSON object.
        """
        return json.loads(
            self.aes_decrypt(request.json().get("data"), encryption_keys["second_key"], encryption_keys["iv"]))

    def get_source_data(self, json_response):
        """
        Extracts the source data from the given JSON response.

        Args:
            json_response (dict): The JSON response to extract the source data from.

        Returns:
            list: A list of source data extracted from the JSON response.
        """
        return [x for x in json_response["source"]]

    def get_streaming_url(self, ep_url):
        """
        Given an episode URL, returns the URL of the video stream.

        Args:
            ep_url (str): The URL of the episode to stream.

        Returns:
            str: The URL of the video stream.
        """
        try:
            # Get the embedded episode URL
            embded_episode_url = self.get_embedded_video_url(ep_url)
            # Get the encryption keys
            encryption_keys = self.get_encryption_key(embded_episode_url)
            # Get the AJAX URL
            self.ajax_url = self.create_ajax_url(embded_episode_url)
            # Get the ID
            id = self.create_id(embded_episode_url)
            # Encrypt the ID
            encrypted_id = self.encrypt_id(id, encryption_keys)
            # Create the data dictionary
            data = self.create_dict_data(
                embded_episode_url, encryption_keys, encrypted_id)
            # Create the headers
            headers = self.create_headers(embded_episode_url)
            # Send the POST request
            request = self.send_post_request(self.ajax_url, data, id, headers)
            # Check if the request was successful
            self.check_response_error(request, request.url)
            # Create the JSON response
            json_response = self.create_json_response(request, encryption_keys)
            # Get the source data
            source_data = self.get_source_data(json_response)
            # Return the stream URL
            return source_data[0]["file"]
        except Exception as e:
            raise Exception(f"Error while getting stream URL: {e}")
