from Config.logs_config import setup_logging
from Config.config import Config
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter, Retry
from Cryptodome.Cipher import AES
from urllib.parse import urlparse, parse_qsl, urlencode, urljoin
import re
import base64
import json


logger = setup_logging('anime_watch', Config.ANIME_WATCH_LOG_PATH)

class UrlInteractions:
    def __init__(self, quality=None):
    

        self.session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.ajax_url = "/encrypt-ajax.php?"
        self.enc_key_api = "https://raw.githubusercontent.com/justfoolingaround/animdl-provider-benchmarks/master/api/gogoanime.json"
        self.mode = AES.MODE_CBC
        self.pad = lambda s: s + chr(len(s) % 16) * (16 - len(s) % 16)
        self.qual = quality.lower().strip("p")  # quality of the video
    def response_err(self, request, url):
        if request.ok:
            pass
        else:
            print(f"Error while requesting {url}: {request.status_code}")
            raise Exception(
                f"Error while requesting {url}: {request.status_code}")

    def loc_err(self, soup, link, element):
        if soup == None:
            print(f"Error while locating {element} in {link}")
            raise Exception(f"Error while locating {element} in {link}")

    def embed_url(self, ep_url):
        """
        Given an episode URL, returns the URL of the embedded video player for that episode.

        Args:
        - ep_url (str): The URL of the episode to get the embedded video player URL for.

        Returns:
        - str: The URL of the embedded video player for the given episode.

        Raises:
        - Exception: If there is an error while getting the embedded video player URL.
        """
        try:

            r = self.session.get(ep_url)

            self.response_err(r, ep_url)

            soup = BeautifulSoup(r.content, "html.parser")

            link = soup.find("a", {"class": "active", "rel": "1"})

            self.loc_err(link, ep_url, "embed-url")
            ep_url = f'https:{link["data-video"]}' if not link["data-video"].startswith(
                "https:") else link["data-video"]
            return ep_url

        except Exception as e:
            logger.error(f"Error while getting embed url: {e}")

    def get_data(self, ep_url):
        """
        Retrieves the data for a given episode URL.

        Args:
            ep_url (str): The URL of the episode to retrieve data for.

        Returns:
            str: The data for the given episode URL.
        """
        request = self.session.get(ep_url)
        soup = BeautifulSoup(request.content, "html.parser")
        crypto = soup.find("script", {"data-name": "episode"})
        self.loc_err(crypto, ep_url, "token")
        return crypto["data-value"]

    def get_enc_key(self, ep_url):
        """
        Retrieves the encryption key for the given episode URL.

        Args:
            ep_url (str): The URL of the episode to retrieve the encryption key for.

        Returns:
            dict: A dictionary containing the encryption key, initialization vector, and second key.
        """
        page = self.session.get(ep_url).text

        keys = re.findall(r"(?:container|videocontent)-(\d+)", page)

        if not keys:
            return {}

        key, iv, second_key = keys
        return {
            "key": key.encode(),
            "iv": iv.encode(),
            "second_key": second_key.encode()
        }

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
            AES.new(key, self.mode, iv=iv).encrypt(self.pad(data).encode())
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
        return (
            AES.new(key, self.mode, iv=iv)
            .decrypt(base64.b64decode(data))
            .strip(b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10")
        )

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
        return self.aes_decrypt(
            self.get_data(
                ep_url), encryption_keys["key"], encryption_keys["iv"]
        ).decode()

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
        return self.session.post(
            url + urlencode(data) + f"&alias={id}", headers=header)

    def send_post_request(self, url, data, id,  header):
        return self.session.post(
            url + urlencode(data) + f"&alias={id}", headers=header)

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

    def stream_url(self, ep_url):
        """
        Given an episode URL, returns the URL of the video stream.

        Args:
            ep_url (str): The URL of the episode to stream.

        Returns:
            str: The URL of the video stream.
        """
        # Get the encryption keys
        encryption_keys = self.get_enc_key(ep_url)
        # Get the AJAX URL
        self.ajax_url = self.create_ajax_url(ep_url)
        # Get the ID
        id = self.create_id(ep_url)
        # Encrypt the ID
        encrypted_id = self.encrypt_id(id, encryption_keys)
        # Create the data dictionary
        data = self.create_dict_data(ep_url, encryption_keys, encrypted_id)
        # Create the headers
        headers = self.create_headers(ep_url)
        # Send the POST request
        request = self.send_post_request(self.ajax_url, data, id, headers)
        # Check if the request was successful
        self.response_err(request, request.url)
        # Create the JSON response
        json_response = self.create_json_response(request, encryption_keys)
        # Get the source data
        source_data = self.get_source_data(json_response)
        # Check if the source data is empty
        self.quality(source_data)
        # Return the stream URL
        return source_data[0]["file"]

    def quality(self, json_data):
        """
        Determines the quality of the video stream based on the user's preference and the available streams.

        Args:
            json_data (list): A list of dictionaries containing information about the available video streams.

        Returns:
            None
        """
        # self.entry.quality = ""

        streams = []
        for i in json_data:
            if "m3u8" in i["file"] or i["type"] == "hls":
                type = "hls"
            else:
                type = "mp4"

            quality = i["label"].replace(" P", "").lower()

            streams.append(
                {"file": i["file"], "type": type, "quality": quality})

        filtered_q_user = list(
            filter(lambda x: x["quality"] == self.qual, streams))
        if filtered_q_user:
            stream = list(filtered_q_user)[0]
        elif self.qual == "best" or self.qual == None:
            stream = streams[-1]
        elif self.qual == "worst":
            stream = streams[0]
        else:
            stream = streams[-1]

        self.quality = stream["quality"]