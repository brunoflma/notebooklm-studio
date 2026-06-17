import sys
from unittest.mock import MagicMock

# Mock dependencies that are not available in the environment
# to allow importing colab.servidor_colab
sys.modules['flask'] = MagicMock()
sys.modules['flask_cors'] = MagicMock()
sys.modules['pyngrok'] = MagicMock()
sys.modules['requests'] = MagicMock()

from colab.servidor_colab import get_timeout, TIMEOUTS

def test_get_timeout_generate():
    """Tests that commands starting with 'generate' return the correct timeout."""
    assert get_timeout("generate report") == 600
    assert get_timeout("generate") == 600

def test_get_timeout_artifact():
    """Tests that commands starting with 'artifact' return the correct timeout."""
    assert get_timeout("artifact wait") == 600
    assert get_timeout("artifact") == 600

def test_get_timeout_ask():
    """Tests that commands starting with 'ask' return the correct timeout."""
    assert get_timeout("ask what is NotebookLM?") == 120
    assert get_timeout("ask") == 120

def test_get_timeout_default():
    """Tests that unknown commands return the default timeout."""
    assert get_timeout("list") == 180
    assert get_timeout("source list") == 180
    assert get_timeout("unknown") == 180

def test_get_timeout_whitespace():
    """Tests that leading/trailing whitespace is ignored."""
    assert get_timeout("  ask  ") == 120
    assert get_timeout("\tgenerate\n") == 600

def test_get_timeout_case_sensitivity():
    """Tests case sensitivity (it is sensitive in the current implementation)."""
    # Prefix matches are case-sensitive as it uses .startswith()
    assert get_timeout("ASK") == 180  # Should return default
