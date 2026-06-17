import pytest
from colab.utils import get_timeout, TIMEOUTS

def test_get_timeout_generate():
    assert get_timeout("generate report") == TIMEOUTS['generate']
    assert get_timeout("generate podcast") == TIMEOUTS['generate']

def test_get_timeout_artifact():
    assert get_timeout("artifact wait") == TIMEOUTS['artifact']

def test_get_timeout_ask():
    assert get_timeout("ask what is this?") == TIMEOUTS['ask']

def test_get_timeout_default():
    assert get_timeout("list notebooks") == TIMEOUTS['default']
    assert get_timeout("unknown command") == TIMEOUTS['default']

def test_get_timeout_strip_and_whitespace():
    assert get_timeout("  generate  ") == TIMEOUTS['generate']
    assert get_timeout("\tartifact") == TIMEOUTS['artifact']
    assert get_timeout("\nask") == TIMEOUTS['ask']

def test_get_timeout_case_sensitivity():
    # The current implementation uses .startswith(prefix) which is case-sensitive
    # TIMEOUTS keys are 'generate', 'artifact', 'ask', 'default'
    assert get_timeout("GENERATE") == TIMEOUTS['default']
