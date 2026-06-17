import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Mocking modules that are not available or cause side effects during import
sys.modules['flask'] = MagicMock()
sys.modules['flask_cors'] = MagicMock()
sys.modules['pyngrok'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['google.colab'] = MagicMock()

# Setup dummy environment for import
os.environ['NGROK_TOKEN'] = 'dummy_token'
AUTH_FILE = 'dummy_storage_state.json'

if not os.path.exists(AUTH_FILE):
    with open(AUTH_FILE, 'w') as f:
        f.write('{"test": "auth"}')

# Patch os.path.exists before importing servidor_colab
with patch('os.path.exists', return_value=True):
    # Import the module to be tested
    import colab.servidor_colab as servidor_colab

class TestSecurityFix(unittest.TestCase):
    @patch('os.path.exists', return_value=True)
    @patch('colab.servidor_colab.AUTH_FILE', AUTH_FILE)
    def test_run_notebooklm_security(self, mock_exists):
        from colab.servidor_colab import run_notebooklm

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout='ok', stderr='')

            # Normal command
            run_notebooklm('list --json')

            # Malicious command
            run_notebooklm('list; echo INJECTED')

            # Check what was actually called
            calls = [call[0][0] for call in mock_run.call_args_list]

            print(f"\nSubprocess calls: {calls}")

            for call in calls:
                if isinstance(call, str):
                    # If it's a string, we check if it's using shell=True style
                    if '; echo INJECTED' in call:
                        self.fail(f"VULNERABILITY DETECTED: Command injection allowed in call: {call}")
                elif isinstance(call, list):
                    # After fix, it should be a list
                    pass

    @patch('os.path.exists', return_value=True)
    @patch('colab.servidor_colab.AUTH_FILE', AUTH_FILE)
    def test_run_notebooklm_functionality(self, mock_exists):
        from colab.servidor_colab import run_notebooklm
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout='ok', stderr='')

            # Test that it still works for normal commands
            res = run_notebooklm('ask "What is this?"')
            self.assertEqual(res.stdout, 'ok')

            # Check arguments
            args = mock_run.call_args[0][0]
            if isinstance(args, list):
                self.assertEqual(args[0], 'notebooklm')
            else:
                self.assertTrue(args.startswith('notebooklm'))

if __name__ == '__main__':
    unittest.main()
