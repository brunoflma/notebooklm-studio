import sys
import os
from unittest.mock import MagicMock, patch, mock_open

# Mock modules to avoid side effects during import
sys.modules['flask'] = MagicMock()
sys.modules['flask_cors'] = MagicMock()
sys.modules['pyngrok'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['google.colab'] = MagicMock()

# Mock os.path.exists for the credentials check
with patch('os.path.exists', return_value=True):
    import colab.servidor_colab as servidor

import json
import unittest

class TestWriteLog(unittest.TestCase):
    def test_write_log_success(self):
        """Verify that write_log correctly writes an entry to the log file."""
        entry = {"status": "ok", "message": "test"}
        m = mock_open()
        with patch("builtins.open", m):
            servidor.write_log(entry)

            m.assert_called_once_with(servidor.LOG_FILE, 'a', encoding='utf-8')
            expected_json = json.dumps(entry, ensure_ascii=False) + '\n'
            m().write.assert_called_once_with(expected_json)

    def test_write_log_exception_handling(self):
        """Verify that write_log suppresses exceptions during file operations."""
        entry = {"status": "error"}
        # Patch open to raise an exception
        with patch("builtins.open", side_effect=IOError("Permission denied")):
            try:
                servidor.write_log(entry)
            except Exception as e:
                self.fail(f"write_log failed to catch exception: {e}")

if __name__ == "__main__":
    unittest.main()
