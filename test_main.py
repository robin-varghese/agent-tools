import unittest
import os
from unittest.mock import patch
from main import app  # Assuming your Flask app is in main.py and named 'app'

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_hello_world_no_name(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Hello World!')

    @patch.dict(os.environ, {"NAME": "TestUser"})
    def test_hello_world_with_name(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Hello TestUser!')

if __name__ == '__main__':
    unittest.main()