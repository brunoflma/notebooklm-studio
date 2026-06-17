import json

def get_logs_logic(lines, n):
    entries = []
    for line in lines[-n:]:
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return entries

def test_get_logs_logic():
    # Test with valid JSON lines
    lines = [
        '{"ts": "2023-10-27T10:00:00", "cmd": "test1"}',
        '{"ts": "2023-10-27T10:01:00", "cmd": "test2"}'
    ]
    expected = [
        {"ts": "2023-10-27T10:00:00", "cmd": "test1"},
        {"ts": "2023-10-27T10:01:00", "cmd": "test2"}
    ]
    assert get_logs_logic(lines, 50) == expected

    # Test with some invalid JSON lines
    lines = [
        '{"ts": "2023-10-27T10:00:00", "cmd": "test1"}',
        'INVALID JSON',
        '{"ts": "2023-10-27T10:01:00", "cmd": "test2"}'
    ]
    expected = [
        {"ts": "2023-10-27T10:00:00", "cmd": "test1"},
        {"ts": "2023-10-27T10:01:00", "cmd": "test2"}
    ]
    assert get_logs_logic(lines, 50) == expected

    # Test with n parameter
    lines = [
        '{"ts": "2023-10-27T10:00:00", "cmd": "test1"}',
        '{"ts": "2023-10-27T10:01:00", "cmd": "test2"}'
    ]
    expected = [
        {"ts": "2023-10-27T10:01:00", "cmd": "test2"}
    ]
    assert get_logs_logic(lines, 1) == expected

    print("Tests passed!")

if __name__ == "__main__":
    test_get_logs_logic()
