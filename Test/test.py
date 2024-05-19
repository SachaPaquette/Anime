import unittest
import sys
import os

# For the EpisodeList.py tests
import curses
from urllib.parse import ParseResult, urlparse

import requests 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from AnimeWatcher.WebOperations import WebInteractions, AnimeInteractions
from AnimeWatcher.VideoPlayer import VideoPlayer
from AnimeWatcher.UrlOperations import UrlInteractions
from AnimeWatcher.EpisodeOperations import EpisodeMenu, Menu
from AnimeWatcher.UserInteractions import UserInteractions
from AnimeWatcher.EpisodesList import animeList, episodesList, displayAnimes, displayEpisodes, curses_anime_list
from Config.config import AnimeWatcherConfig, WebOperationsConfig
import sys
from io import StringIO
from unittest.mock import patch, MagicMock, Mock
from bs4 import BeautifulSoup

class TestEpisodeOperations(unittest.TestCase):
    
    def __init__(self, *args, **kwargs):
        super(TestEpisodeOperations, self).__init__(*args, **kwargs)
        self.user_interactions = UserInteractions()
        start_episode = 1
        max_episode = 5
        self.episode_menu = EpisodeMenu(start_episode, max_episode)
        self.captured_output = StringIO()
        self.current_episode = 3
        # Available menu choices for the episode menu
        self.available_menu_choices = ['n', 'p', 'c', 'q']
        
    def test_StartEpisodeEqualsMaxEpisode(self):
        # Test that the start episode is equal to the max episode
        episode_menu = EpisodeMenu(5, 5)
        self.assertEqual(episode_menu.start_episode, episode_menu.max_episode)
    
    def test_NextEpisodeOnLastEpisode(self):
        current_episode = 5
        expected_output = "No more episodes available."
        sys.stdout = self.captured_output
        episode = self.episode_menu.handle_choice(Menu.NextEpisode, current_episode)
        sys.stdout = sys.__stdout__
        output = self.captured_output.getvalue().strip()
        # Check that the expected console output is returned
        self.assertEqual(output, expected_output)
        # Check that the current episode is returned when the user is at the last episode
        self.assertEqual(episode, current_episode)
        
    def test_NextEpisodeSuccess(self):      
        next_episode = self.episode_menu.handle_choice(Menu.NextEpisode, self.current_episode)
        self.assertEqual(next_episode, self.current_episode + 1)
        
    def test_PreviousEpisodeSuccess(self):
        previous_episode = self.episode_menu.handle_choice(Menu.PreviousEpisode, self.current_episode)
        self.assertEqual(previous_episode, self.current_episode - 1)
        
    def test_PreviousEpisodeOnFirstEpisode(self):
        # Expected console output when the user is at the first episode
        expected_output = "Already at the first episode."
        sys.stdout = self.captured_output
        
        # Test previous episode when the user is at the first episode
        previous_episode = self.episode_menu.handle_choice(Menu.PreviousEpisode, 1)
        sys.stdout = sys.__stdout__
        
        self.assertEqual(previous_episode, 1)
        
        self.assertEqual(self.captured_output.getvalue().strip(), expected_output)
    
    def test_Quit(self):
        quit_episode = self.episode_menu.handle_choice(Menu.Quit, self.current_episode)
        # Check that the output is 'q' 
        self.assertEqual(quit_episode, Menu.Quit)
        # Test the type of the output
        self.assertIsInstance(quit_episode, str)


    def test_ChangeAnime(self):
        change_anime = self.episode_menu.handle_choice(Menu.ChangeAnime, self.current_episode)
        # Check that the output is 'c'
        self.assertEqual(change_anime, Menu.ChangeAnime)
        # Test the type of the output
        self.assertIsInstance(change_anime, str)

    def test_InvalidChoice(self):      
        # Expected console output
        expected_output = f"Invalid choice. Please enter one of the following: {', '.join(self.episode_menu.available_choices())}."
        sys.stdout = self.captured_output
        
        # Test invalid choice
        invalid_choice = self.episode_menu.handle_choice('x', self.current_episode)
        sys.stdout = sys.__stdout__
        # Get the console output
        output = self.captured_output.getvalue().strip()
        # Compare the console output with the expected output
        self.assertEqual(output, expected_output)
        # Test that the current episode is returned when the user enters an invalid choice
        self.assertEqual(invalid_choice, self.current_episode)

    def test_MenuChoices(self):
        # Get the available menu choices
        available_choices = self.episode_menu.available_choices()
        # Check that the available choices are 'n', 'p', 'q', and 'c'
        self.assertEqual(available_choices, self.available_menu_choices)

    def test_MenuChoicesType(self):
        # Get the available menu choices
        available_choices = self.episode_menu.available_choices()
        # Check that the available choices are of type list
        self.assertIsInstance(available_choices, list)
            
    def test_NextEpisodeType(self):
        # Test that the next episode is of type int
        next_episode = self.episode_menu.handle_choice(Menu.NextEpisode, self.current_episode)
        self.assertIsInstance(next_episode, int)
    
    def test_PreviousEpisodeType(self):
        # Test that the previous episode is of type int
        previous_episode = self.episode_menu.handle_choice(Menu.PreviousEpisode, self.current_episode)
        self.assertIsInstance(previous_episode, int)
        
    def test_MenuChoicesLength(self):
        # Get the available menu choices
        available_choices = self.episode_menu.available_choices()
        # Check that the available choices are of length 4
        self.assertEqual(len(available_choices), 4)
        
    def test_MenuChoicesType(self):
        # Test that all the available menu choices are of type str
        available_choices = self.episode_menu.available_choices()
        for choice in available_choices:
            self.assertIsInstance(choice, str)
        
    def test_DisplayMenu(self):
        # Redirect the console output to the captured_output variable
        sys.stdout = self.captured_output
        # Expected menu output
        expected_output = (
        "\033c"
        "===== Menu =====\n"
        f"{self.episode_menu.color.green}[N] Next Episode{self.episode_menu.color.endc}\n"
        f"{self.episode_menu.color.yellow}[P] Previous Episode{self.episode_menu.color.endc}\n"
        f"{self.episode_menu.color.orange}[C] Change Anime{self.episode_menu.color.endc}\n"
        f"{self.episode_menu.color.red}[Q] Quit{self.episode_menu.color.endc}"
        )
        
        # Display the menu
        self.episode_menu.display_menu()
        # Get the console output
        sys.stdout = sys.__stdout__
        output = self.captured_output.getvalue().strip()
        # Compare the console output with the expected output
        self.assertEqual(output, expected_output)
    
"""
class TestEpisodeList(unittest.TestCase):
 
    def setUp(self):
        self.stdscr = curses.initscr()
        self.max_episode = 10
        self.cursor = 0
        self.expected_output = [
            "> 1\n",
            "  2\n",
            "  3\n",
            "  4\n",
            "  5\n",
            "  6\n",
            "  7\n",
            "  8\n",
            "  9\n",
            "  10\n"
        ]
        self.mock_stdscr = MagicMock(spec=curses.window)
        self.episode_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    def tearDown(self):
        curses.endwin()

    def testDisplayAnimes(self):
        anime = [{'title': 'Naruto'}, {'title': 'One Piece'}, {'title': 'Bleach'}]
        cursor = 0
        expected_output = [
            "> 1. Naruto\n",
            "  2. One Piece\n",
            "  3. Bleach\n"
        ]
        with patch.object(self.stdscr, 'addstr') as mock_addstr:
            displayAnimes(self.stdscr, anime, cursor)
            for i, line in enumerate(expected_output):
                mock_addstr.assert_any_call(i, 0, line)  # Adjusted index here

            


    def testDisplayEpisodes(self):
        displayEpisodes(self.stdscr, self.episode_list, self.cursor)
        

    def testCursesAnimeList(self):
        animes = [{'title': 'Naruto'}, {'title': 'One Piece'}, {'title': 'Bleach'}]
        cursor = 0
        expected_cursor = 1
        with patch('curses.wrapper') as mock_wrapper:
            mock_wrapper.return_value = expected_cursor
            selected_index = curses_anime_list(self.stdscr, animes, displayAnimes)
            self.assertEqual(selected_index, expected_cursor)
        """
class TestUrlOperations(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Create an instance of the UrlInteractions class
        cls.url_interactions = UrlInteractions()
        
        # URLs
        cls.embedded_url = 'https://embtaku.pro/streaming.php?id=MjUwNTQ=&title=Naruto+Episode+1&typesub=SUB'
        cls.embedded_url_com = 'https://embtaku.com/streaming.php?id=MjUwNTQ=&title=Naruto+Episode+1&typesub=SUB'
        cls.episode_url = 'https://gogoanime3.net/naruto-episode-1'
        cls.ajax_url = 'https://embtaku.pro/encrypt-ajax.php?'
        cls.streaming_url = 'https://www084.vipanicdn.net/streamhls/027e9529af2b06fe7b4f47e507a787eb/ep.1.1703905435.m3u8'
        
        # Expected information for the encryption keys
        cls.first_key = b'37911490979715163134003223491201'
        cls.first_key_iv = b'3134003223491201'
        cls.second_key = b'54674138327930866480207815084989'
        cls.expected_keys = {'key': cls.first_key, 'iv': cls.first_key_iv, 'second_key': cls.second_key}
        
        cls.expected_decrypted_url = 'MjUwNTQ=&title=Naruto+Episode+1&typesub=SUB&mip=0.0.0.0&refer=none&ch=d41d8cd98f00b204e9800998ecf8427e'
        cls.expected_id = 'MjUwNTQ='
        cls.expected_encrypted_id = 'BrAN784pvn7nL4c8U3x03Q=='
        cls.expected_data = {'id': cls.expected_encrypted_id}
        
        # Expected headers
        cls.expected_headers = {
            "x-requested-with": "XMLHttpRequest",
            "referer": cls.embedded_url,
        }
        cls.expected_headers_com = {
            "x-requested-with": "XMLHttpRequest",
            "referer": cls.embedded_url_com,
        }
        # Get the encryption keys
        cls.keys = cls.url_interactions.get_encryption_keys(cls.embedded_url)
        # Create a dictionary data
        cls.dict_data = cls.url_interactions.create_dict_data(cls.embedded_url_com, cls.keys, cls.expected_encrypted_id)
        
        # Make a POST request to the URL
        cls.request = cls.url_interactions.send_post_request(cls.ajax_url, cls.dict_data, cls.expected_id, cls.expected_headers_com)
        
    def tearDown(self):
        self.url_interactions.close_session()
                
    def test_get_request(self):
        # Make a GET request to the URL
        request = self.url_interactions.session.get(self.episode_url)
        # Check that the request is not None
        self.assertIsNotNone(request)
        # Check that the request is of type Response
        self.assertIsInstance(request, requests.models.Response)
        # Check that the request has a status of 200
        self.assertEqual(request.status_code, 200)
        # Check that the request has a reason of 'OK'
        self.assertEqual(request.reason, 'OK')
        # Check that the request has a URL of 'https://gogoanime3.co/naruto-episode-1'
        self.assertEqual(request.url, 'https://gogoanime3.co/naruto-episode-1')
  
                
    def test_get_soup_object(self):
        # Get the soup object
        soup = self.url_interactions.get_soup_object(self.episode_url)
        # Check that the soup object is not None
        self.assertIsNotNone(soup)
        # Check that the soup object is of type BeautifulSoup
        self.assertIsInstance(soup, BeautifulSoup)
        # Check that the title of the page is 'Watch Naruto Episode 1 English Subbed at Gogoanime'
        self.assertEqual(soup.title.string, 'Watch Naruto Episode 1 English Subbed at Gogoanime')


    def test_create_embedded_url(self):
        # Create an active link with the episode URL
        active_link = BeautifulSoup(f'<a data-video="{self.episode_url}"></a>', 'html.parser').a
        # Create an embedded URL
        embedded_url = self.url_interactions.create_embedded_url(active_link)
        # Check that the embedded URL is not None
        self.assertIsNotNone(embedded_url)
        # Check that the embedded URL is of type str
        self.assertIsInstance(embedded_url, str)
        # Check that the embedded URL is 'https://gogoanime3.net/naruto-episode-1'
        self.assertEqual(embedded_url, self.episode_url)

    def test_get_embedded_video_url(self):
        # Get the embedded URL
        embedded_url = self.url_interactions.get_embedded_video_url(self.episode_url)
        # Check that the embedded URL is not None
        self.assertIsNotNone(embedded_url)
        # Check that the embedded URL is of type str
        self.assertIsInstance(embedded_url, str)
        # Check that the embedded URL is 'https://embtaku.pro/streaming.php?id=MjUwNTQ=&title=Naruto+Episode+1&typesub=SUB'
        self.assertEqual(embedded_url, self.embedded_url_com)
        
        
    
    def test_get_encryption_keys(self):
        # Check that the keys are not None
        self.assertIsNotNone(self.keys)
        # Check that the keys are of type dict
        self.assertIsInstance(self.keys, dict)

        # Check that the keys are as expected
        self.assertEqual(self.keys, self.expected_keys)
        # Check that the structure of the dictionary is as expected
        self.assertEqual(self.keys.keys(), self.expected_keys.keys())
       
    
    def test_decrypt_url(self):
        # Decrypt the video URL
        decrypted_video_url = self.url_interactions.decrypt_url(self.embedded_url, self.keys)
        # Check that the decrypted video URL is not None
        self.assertIsNotNone(decrypted_video_url)
        # Check that the decrypted video URL is of type str
        self.assertIsInstance(decrypted_video_url, str)
        # Check that the expected decrypted video URL is contained in the decrypted video URL (since we can't directly compare the two URLs due to the fact that the token changes every time the URL is decrypted)
        self.assertIn(self.expected_decrypted_url, decrypted_video_url) 
    
    
    def test_urlparse(self):
        # Parse the URL
        parsed_url = urlparse(self.embedded_url)
        # Check that the parsed URL is not None
        self.assertIsNotNone(parsed_url)
        # Check that the parsed URL is of type tuple
        self.assertIsInstance(parsed_url, tuple)
        expected_parsed_url = ParseResult(scheme='https', netloc='embtaku.pro', path='/streaming.php', params='', query='id=MjUwNTQ=&title=Naruto+Episode+1&typesub=SUB', fragment='')
        # Check that the scheme of the parsed URL is 'https'
        self.assertEqual(parsed_url.scheme, expected_parsed_url.scheme)
        # Check that the netloc of the parsed URL is 'embtaku.pro'
        self.assertEqual(parsed_url.netloc, expected_parsed_url.netloc)
        # Check that the path of the parsed URL is '/streaming.php'
        self.assertEqual(parsed_url.path, expected_parsed_url.path)
        # Check that the params of the parsed URL is ''
        self.assertEqual(parsed_url.params, expected_parsed_url.params)
        # Check that the query of the parsed URL is 'id=MjUwNTQ=&title=Naruto+Episode+1&typesub=SUB'
        self.assertEqual(parsed_url.query, expected_parsed_url.query)
        # Check that the fragment of the parsed URL is ''
        self.assertEqual(parsed_url.fragment, expected_parsed_url.fragment)
        # Check that the parsed URL has the expected length
        self.assertEqual(len(parsed_url), len(expected_parsed_url))
        # Check that the parsed URL is as expected
        self.assertEqual(parsed_url, expected_parsed_url)
    
    def test_create_ajax_url(self):  
        # Create an AJAX URL
        ajax_url = self.url_interactions.create_ajax_url(self.embedded_url)
        # Check that the AJAX URL is not None
        self.assertIsNotNone(ajax_url)
        # Check that the AJAX URL is of type str
        self.assertIsInstance(ajax_url, str)
        # Check that the AJAX URL is 'https://embtaku.pro/encrypt-ajax.php?'
        self.assertEqual(ajax_url, self.ajax_url)
    
    def test_create_id(self):
        # Create an ID
        id = self.url_interactions.create_id(self.embedded_url)
        # Check that the ID is not None
        self.assertIsNotNone(id)
        # Check that the ID is of type str
        self.assertIsInstance(id, str)
        # Check that the ID is 'MjUwNTQ='
        self.assertEqual(id, self.expected_id)
        
    def test_encrypt_id(self):
        # Encrypt the ID
        encrypted_id = self.url_interactions.encrypt_id(self.expected_id, self.keys)
        # Check that the encrypted ID is not None
        self.assertIsNotNone(encrypted_id)
        # Check that the encrypted ID is of type str
        self.assertIsInstance(encrypted_id, str)
        # Check that the encrypted ID is 'BrAN784pvn7nL4c8U3x03Q=='
        self.assertEqual(encrypted_id, self.expected_encrypted_id)
        
    def test_create_dict_data(self):
        # Mock the necessary methods and attributes

        # Call the method under test
  
        # Assert the expected result
        expected_result = {
            'title': 'Naruto Episode 1',
            'typesub': 'SUB',
            'mip': '0.0.0.0',
            'refer': 'none',
            'ch': 'd41d8cd98f00b204e9800998ecf8427e',
            'token2': '',
            'expires2': '',
            'op': '1',
            'id': 'BrAN784pvn7nL4c8U3x03Q=='
        }
        # Check that the dictionary data is not None
        self.assertIsNotNone(self.dict_data)
        
        # Check that the dictionary data is of type dict
        self.assertIsInstance(self.dict_data, dict)
        
        # Check that there are no missing keys
        self.assertEqual(self.dict_data.keys(), expected_result.keys())
        
        # Check that the dictionary data is as expected
        self.assertEqual(self.dict_data["title"], expected_result["title"])
        self.assertEqual(self.dict_data["typesub"], expected_result["typesub"])
        self.assertEqual(self.dict_data["mip"], expected_result["mip"])
        self.assertEqual(self.dict_data["refer"], expected_result["refer"])
        self.assertEqual(self.dict_data["ch"], expected_result["ch"])
        self.assertEqual(self.dict_data["op"], expected_result["op"])
        self.assertEqual(self.dict_data["id"], expected_result["id"])
        
    def test_aes_encrypt(self):
        # Data to be encrypted
        data = "Hello, World!"
        # Key and IV
        key = b"0123456789abcdef"
        iv = b"fedcba9876543210"
        # Expected result
        expected_result = b'+cOybNzMzoXqqScNJeAP+A=='
        # Encrypt the data
        encrypted_data = self.url_interactions.aes_encrypt(data, key, iv)
        # Check that the encrypted data is not None
        self.assertIsNotNone(encrypted_data)
        # Check that the encrypted data is of type bytes
        self.assertIsInstance(encrypted_data, bytes)
        # Check that the encrypted data is as expected
        self.assertEqual(encrypted_data, expected_result)

        
    def test_create_headers(self):
        headers = self.url_interactions.create_headers(self.embedded_url)
        
        # Check that the headers are not None
        self.assertIsNotNone(headers)
        # Check that the headers are of type dict
        self.assertIsInstance(headers, dict)
        # Check that the headers are as expected
        self.assertEqual(headers, self.expected_headers)
        
    # Define a method to compare URLs
    def assertUrlsSimilar(self, url1, url2):
        domain1 = url1.split('/')[2]
        domain2 = url2.split('/')[2]
        path1 = '/'.join(url1.split('/')[-3:])
        path2 = '/'.join(url2.split('/')[-3:])
        return domain1 == domain2 and path1 == path2
    def test_send_post_request(self):
        # Check that the result is not None
        self.assertIsNotNone(self.request)
        # Check that the result is of type Response
        self.assertIsInstance(self.request, requests.models.Response)
        # Check that the result has a status of 200
        self.assertEqual(self.request.status_code, 200)
        # Check that the result has a reason of 'OK'
        self.assertEqual(self.request.reason, 'OK')
    def test_check_response_error(self):
        # Check that the response is not an error
        self.assertFalse(self.url_interactions.check_response_error(self.request, self.request.url))
        
        
    def test_get_streaming_url(self):
            # Get the streaming URL
            streaming_url = self.url_interactions.get_streaming_url(self.episode_url)
            # Check that the streaming URL is not None
            self.assertIsNotNone(streaming_url)
            # Check that the streaming URL is of type str
            self.assertIsInstance(streaming_url, str)
            # Check that the streaming URL is 'https://www084.vipanicdn.net/streamhls/027e9529af2b06fe7b4f47e507a787eb/ep.1.1703905435.m3u8'
            self.assertEqual(streaming_url, self.streaming_url)
            
    def test_create_json_response(self):  
   
        print('request', self.request.content)
        # Decrypt the result
        json_response = self.url_interactions.create_json_response(self.request, self.keys)
        # Check that the result is not None
        self.assertIsNotNone(json_response)
        # Check that the result is of type dict
        self.assertIsInstance(json_response, dict)

    
        expected_result = {'source': [{'file': 'https://www084.vipanicdn.net/streamhls/027e9529af2b06fe7b4f47e507a787eb/ep.1.1703905435.m3u8', 
                                       'label': 'hls P', 'type': 'hls'}], 
                           'source_bk': [{'file': 'https://www084.anicdnstream.info/videos/hls/oQQliQuPlfRAUSxuJNB3rw/1715569478/25054/027e9529af2b06fe7b4f47e507a787eb/ep.1.1703905435.m3u8', 
                                          'label': 'hls P', 'type': 'hls'}],
                           'track': [], 
                           'advertising': [], 
                           'linkiframe': 'https://awish.pro/e/55n21er26pfb'}

        # Check that the result contains a 'source' key
        self.assertIn('source', json_response)
        # Check that the source length is as expected
        self.assertEqual(len(json_response['source']), len(expected_result['source']))
        # Check that the result contains a 'source_bk' key
        self.assertIn('source_bk', json_response)
        # Check that the source_bk length is as expected
        self.assertEqual(len(json_response['source_bk']), len(expected_result['source_bk']))
        # Check that the result contains a 'track' key
        self.assertIn('track', json_response)
        # Check that the track length is as expected
        self.assertEqual(len(json_response['track']), len(expected_result['track']))
        # Check that the result contains a 'advertising' key
        self.assertIn('advertising', json_response)
        # Check that the advertising length is as expected
        self.assertEqual(len(json_response['advertising']), len(expected_result['advertising']))
        # Check that the result contains a 'linkiframe' key
        self.assertIn('linkiframe', json_response)
        # Check that the linkiframe is as expected
        self.assertEqual(json_response['linkiframe'], expected_result['linkiframe'])

        for src1, src2 in zip(json_response['source'], expected_result['source']):
            self.assertTrue(self.assertUrlsSimilar(src1['file'], src2['file']))
            self.assertEqual(src1['label'], src2['label'])
            self.assertEqual(src1['type'], src2['type'])
        for src_bk1, src_bk2 in zip(json_response['source_bk'], expected_result['source_bk']):
            self.assertTrue(self.assertUrlsSimilar(src_bk1['file'], src_bk2['file']))
            self.assertEqual(src_bk1['label'], src_bk2['label'])
            self.assertEqual(src_bk1['type'], src_bk2['type'])

   
"""    def test_create_json_response(self):
        # Create a mock request object
        request = Mock()
        # Set the json method of the request object to return a mock JSON response
        request.json.return_value = {"data": "encrypted_data"}
        
        # Call the create_json_response method with the mock request and encryption keys
        result = self.url_interactions.create_json_response(request, self.expected_keys)
        # Assert that the result is not None
        self.assertIsNotNone(result)
        
        # Assert that the result is equal to the decrypted JSON object
        self.assertEqual(result, {"decrypted_data": "decrypted_data"})

        """

if __name__ == "__main__":
    unittest.main()