import sys
from unittest.mock import MagicMock, patch

# Define a decorator that returns the function unchanged
def identity_decorator(*args, **kwargs):
    def wrapper(f):
        return f
    return wrapper

# Mock modules
mock_flask = MagicMock()
mock_flask_cors = MagicMock()
mock_pyngrok = MagicMock()
mock_requests = MagicMock()

# Configure Flask mock
mock_flask.Flask.return_value.route.side_effect = identity_decorator

sys.modules['flask'] = mock_flask
sys.modules['flask_cors'] = mock_flask_cors
sys.modules['pyngrok'] = mock_pyngrok
sys.modules['requests'] = mock_requests

# Now import the module to test
import colab.servidor_colab as servidor

def test_health():
    """Test that the health endpoint returns {'status': 'ok'}."""
    # Patch jsonify within the imported module
    with patch('colab.servidor_colab.jsonify') as mock_jsonify:
        mock_jsonify.side_effect = lambda x: x

        response = servidor.health()

        assert response == {'status': 'ok'}
        mock_jsonify.assert_called_once_with({'status': 'ok'})
