#!/bin/env python3

import unittest
import os
import tempfile
import yaml
from io import StringIO
from unittest.mock import patch, MagicMock
import slowdownloader

class TestSlowDownloader(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        # Clean up the temporary directory
        self.test_dir.cleanup()

    def test_getargs(self):
        # Test argument parsing
        with patch('sys.argv', ['slowdownloader.py', '-f', 'urls.yaml', '-t', '100', '--ipv4']):
            args = slowdownloader.getargs()
            self.assertEqual(args.urlfile, 'urls.yaml')
            self.assertEqual(args.timeout, 100)
            self.assertTrue(args.ipv4)

    def test_loadurls(self):
        # Test loading URLs from a YAML file
        yaml_content = """
        file1:
            url: http://example.com/file1.zip
            filename: file1.zip
        file2:
            url: http://example.com/file2.zip
        """
        expected_urls = {
            'file1': {'url': 'http://example.com/file1.zip', 'filename': 'file1.zip'},
            'file2': {'url': 'http://example.com/file2.zip'}
        }

        # Create a temporary YAML file
        yaml_file = os.path.join(self.test_dir.name, 'urls.yaml')
        with open(yaml_file, 'w') as f:
            f.write(yaml_content)

        # Load URLs from the file
        urls = slowdownloader.loadurls(yaml_file)
        self.assertEqual(urls, expected_urls)

    def test_loadurls_file_not_found(self):
        # Test handling of a non-existent file
        with self.assertRaises(SystemExit):
            slowdownloader.loadurls('nonexistent.yaml')

    @patch('pycurl.Curl')
    def test_downloadfile(self, mock_curl):
        # Test downloading a file
        mock_curl_instance = MagicMock()
        mock_curl.return_value = mock_curl_instance

        url = 'http://example.com/file1.zip'
        filename = os.path.join(self.test_dir.name, 'file1.zip')
        timeout = 100

        slowdownloader.downloadfile(url, filename, timeout, False)

        # Check if the Curl options were set correctly
        mock_curl_instance.setopt.assert_any_call(mock_curl_instance.URL, url)
        mock_curl_instance.setopt.assert_any_call(mock_curl_instance.USERAGENT, 'curl/7.45.0')
        mock_curl_instance.setopt.assert_any_call(mock_curl_instance.TIMEOUT, timeout)
        mock_curl_instance.perform.assert_called_once()
        mock_curl_instance.close.assert_called_once()

    @patch('pycurl.Curl')
    def test_downloadfile_ipv4(self, mock_curl):
        # Test downloading a file with ipv4=True
        mock_curl_instance = MagicMock()
        mock_curl.return_value = mock_curl_instance

        url = 'http://example.com/file1.zip'
        filename = os.path.join(self.test_dir.name, 'file1.zip')
        timeout = 100

        slowdownloader.downloadfile(url, filename, timeout, True)

        # Check if the Curl options were set correctly
        mock_curl_instance.setopt.assert_any_call(mock_curl_instance.URL, url)
        mock_curl_instance.setopt.assert_any_call(mock_curl_instance.USERAGENT, 'curl/7.45.0')
        mock_curl_instance.setopt.assert_any_call(mock_curl_instance.TIMEOUT, timeout)
        mock_curl_instance.setopt.assert_any_call(mock_curl_instance.IPRESOLVE, mock_curl_instance.IPRESOLVE_V4)
        mock_curl_instance.perform.assert_called_once()
        mock_curl_instance.close.assert_called_once()

    @patch('slowdownloader.downloadfile')
    def test_downloader(self, mock_downloadfile):
        # Test the downloader function
        urls = {
            'file1': {'url': 'http://example.com/file1.zip', 'filename': 'file1.zip'},
            'file2': {'url': 'http://example.com/file2.zip'}
        }
        default_timeout = 100

        slowdownloader.downloader(urls, default_timeout, False)

        # Check if downloadfile was called with the correct arguments
        mock_downloadfile.assert_any_call('http://example.com/file1.zip', 'file1.zip', default_timeout, False)
        mock_downloadfile.assert_any_call('http://example.com/file2.zip', 'file2.zip', default_timeout, False)

    @patch('slowdownloader.downloadfile')
    def test_downloader_ipv4(self, mock_downloadfile):
        # Test the downloader function with ipv4=True
        urls = {
            'file1': {'url': 'http://example.com/file1.zip', 'filename': 'file1.zip'}
        }
        default_timeout = 100

        slowdownloader.downloader(urls, default_timeout, True)

        # Check if downloadfile was called with the correct arguments
        mock_downloadfile.assert_called_once_with('http://example.com/file1.zip', 'file1.zip', default_timeout, True)

    @patch('os.getenv', return_value='1')
    @patch('sys.argv', ['slowdownloader.py', '-f', 'urls.yaml', '-t', '100'])
    @patch('slowdownloader.loadurls')
    @patch('slowdownloader.downloader')
    def test_main(self, mock_downloader, mock_loadurls, mock_getenv):
        # Test the main function
        mock_loadurls.return_value = {
            'file1': {'url': 'http://example.com/file1.zip', 'filename': 'file1.zip'}
        }

        slowdownloader.main()

        # Check if DEBUG is active
        self.assertTrue(slowdownloader.DEBUG)

        # Check if loadurls and downloader were called
        mock_loadurls.assert_called_once_with('urls.yaml')
        mock_downloader.assert_called_once_with(mock_loadurls.return_value, 100, False)

if __name__ == '__main__':
    unittest.main()
