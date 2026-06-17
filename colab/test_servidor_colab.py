import unittest
import os
import json
import subprocess
import tempfile
import sys
from unittest.mock import MagicMock, patch

# Mock dependencies for servidor_colab
mock_flask_mod = MagicMock()
sys.modules['flask'] = mock_flask_mod
sys.modules['flask_cors'] = MagicMock()
sys.modules['pyngrok'] = MagicMock()
sys.modules['google.colab'] = MagicMock()
sys.modules['requests'] = MagicMock()

# Setup Flask mock to keep original functions
def mock_route(*args, **kwargs):
    def decorator(f):
        return f
    return decorator

mock_app = MagicMock()
mock_flask_mod.Flask.return_value = mock_app
mock_app.route = mock_route

# Mock jsonify to return its input
mock_flask_mod.jsonify = lambda x: x

# Now import the module
import colab.servidor_colab as servidor

class TestGetLogs(unittest.TestCase):
    def setUp(self):
        self.test_log = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl')
        self.log_path = self.test_log.name
        self.old_log_file = servidor.LOG_FILE
        servidor.LOG_FILE = self.log_path

    def tearDown(self):
        servidor.LOG_FILE = self.old_log_file
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    @patch('colab.servidor_colab.request')
    def test_get_logs_basic(self, mock_request):
        for i in range(100):
            self.test_log.write(json.dumps({'i': i}) + '\n')
        self.test_log.close()

        # Mock request.args.get
        mock_request.args.get.return_value = '50'

        result = servidor.get_logs()
        logs = result['logs']

        self.assertEqual(len(logs), 50)
        self.assertEqual(logs[0]['i'], 50)
        self.assertEqual(logs[-1]['i'], 99)

    @patch('colab.servidor_colab.request')
    def test_get_logs_with_empty_lines(self, mock_request):
        for i in range(10):
            self.test_log.write(json.dumps({'i': i}) + '\n')
            self.test_log.write('\n')
        self.test_log.close()

        mock_request.args.get.return_value = '5'

        result = servidor.get_logs()
        logs = result['logs']

        self.assertEqual(len(logs), 5)
        self.assertEqual(logs[-1]['i'], 9)
        self.assertEqual(logs[0]['i'], 5)

    def test_get_logs_file_not_found(self):
        os.remove(self.log_path)
        result = servidor.get_logs()
        self.assertEqual(result['logs'], [])

    @patch('colab.servidor_colab.request')
    def test_get_logs_corrupted_json(self, mock_request):
        self.test_log.write(json.dumps({'i': 1}) + '\n')
        self.test_log.write('invalid json\n')
        self.test_log.write(json.dumps({'i': 2}) + '\n')
        self.test_log.close()

        mock_request.args.get.return_value = '10'
        result = servidor.get_logs()
        logs = result['logs']

        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0]['i'], 1)
        self.assertEqual(logs[1]['i'], 2)

if __name__ == '__main__':
    unittest.main()
