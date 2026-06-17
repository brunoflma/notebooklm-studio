const { cleanOutput, stripCliTables, extractTableValues } = require('./utils');

describe('cleanOutput', () => {
  test('should return empty string for null or undefined input', () => {
    expect(cleanOutput(null)).toBe('');
    expect(cleanOutput(undefined)).toBe('');
  });

  test('should remove ASCII table borders', () => {
    const input = '┏━━━━━━━┳━━━━━━━━┓\n┃ Key   ┃ Value  ┃\n┣━━━━━━━╋━━━━━━━━┫\n┃ Test  ┃ Pass   ┃\n┗━━━━━━━┻━━━━━━━━┛';
    const output = cleanOutput(input);
    expect(output).not.toContain('┏');
    expect(output).not.toContain('┣');
    expect(output).not.toContain('┗');
    expect(output).toContain('Key');
    expect(output).toContain('Value');
    expect(output).toContain('Test');
    expect(output).toContain('Pass');
  });

  test('should remove CLI system headers', () => {
    const input = 'Continuing conversation\nResumed conversation\nStarted: 123\nMatched: xyz\nReal content';
    const output = cleanOutput(input);
    expect(output).toBe('Real content');
  });

  test('should remove excessive blank lines', () => {
    const input = 'Line 1\n\n\n\nLine 2';
    const output = cleanOutput(input);
    expect(output).toBe('Line 1\n\nLine 2');
  });

  test('should trim the output', () => {
    const input = '   \n  Some text  \n  \n';
    const output = cleanOutput(input);
    expect(output).toBe('Some text');
  });
});

describe('stripCliTables', () => {
  test('should remove table border lines but keep content lines', () => {
    const input = '┌──────┐\n│ Text │\n└──────┘';
    const output = stripCliTables(input);
    expect(output).toBe('│ Text │');
  });
});

describe('extractTableValues', () => {
  test('should extract values from simple ASCII table', () => {
    const input = '│ Title  │ My Notebook │\n│ ID     │ 123456      │';
    const values = extractTableValues(input);
    expect(values).toEqual({
      'title': 'My Notebook',
      'id': '123456'
    });
  });

  test('should handle empty input', () => {
    expect(extractTableValues('')).toEqual({});
  });

  test('should ignore table separators', () => {
    const input = '│ Key   │ Value │\n├───────┼───────┤\n│ Test  │ OK    │';
    const values = extractTableValues(input);
    expect(values).toEqual({
      'key': 'Value',
      'test': 'OK'
    });
  });
});
