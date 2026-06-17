import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import os
import sys

# Mock modules that might not be available
mock_flask = MagicMock()
sys.modules['flask'] = mock_flask
sys.modules['flask_cors'] = MagicMock()
sys.modules['pyngrok'] = MagicMock()
sys.modules['google.colab'] = MagicMock()
sys.modules['requests'] = MagicMock()

# Configure mock_flask to return the original function for route decorators
def identity_decorator(*args, **kwargs):
    def wrapper(f):
        return f
    return wrapper
mock_flask.Flask.return_value.route = identity_decorator

# Import the code to test
with patch('os.path.exists', return_value=True):
    with patch('builtins.open', mock_open(read_data='{"auth": "token"}')):
        with patch('pyngrok.ngrok.connect') as mock_connect:
            mock_connect.return_value.public_url = "http://mock.ngrok.io"
            import colab.servidor_colab as servidor

class TestServidorColab(unittest.TestCase):

    def setUp(self):
        servidor.LOG_FILE = 'test_log.jsonl'

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dumps')
    def test_write_log_success(self, mock_json_dumps, mock_file):
        mock_json_dumps.return_value = '{"test": "data"}'
        servidor.write_log({"test": "data"})
        mock_file.assert_called_with('test_log.jsonl', 'a', encoding='utf-8')
        mock_file().write.assert_called_with('{"test": "data"}\n')

    @patch('builtins.open', side_effect=OSError("Permission denied"))
    def test_write_log_failure(self, mock_file):
        with patch.object(servidor.app.logger, 'error') as mock_log_error:
            servidor.write_log({"test": "data"})
            mock_log_error.assert_called()
            self.assertIn("Erro ao escrever log", mock_log_error.call_args[0][0])

    @patch('os.path.exists', return_value=True)
    def test_get_logs_skips_invalid_json(self, mock_exists):
        # Directly patch the symbols in the servidor module
        with patch('colab.servidor_colab.request') as mock_request, \
             patch('colab.servidor_colab.jsonify') as mock_jsonify:

            mock_request.args.get.return_value = 50

            # Mock the file content
            content = '{"valid": "json"}\ninvalid_json\n{"another": "valid"}'
            with patch('builtins.open', mock_open(read_data=content)):
                # Now we call the handler directly
                servidor.get_logs()

                # Check what was passed to jsonify
                self.assertTrue(mock_jsonify.called, "jsonify was not called")
                args, kwargs = mock_jsonify.call_args
                entries = args[0]['logs']
                self.assertEqual(len(entries), 2)
                self.assertEqual(entries[0], {"valid": "json"})
                self.assertEqual(entries[1], {"another": "valid"})

if __name__ == '__main__':
    unittest.main()
