/**
 * Utility functions for NotebookLM Studio
 */

/**
 * Removes CLI table borders and excessive blank lines.
 * @param {string} text
 * @returns {string}
 */
function stripCliTables(text) {
  if (!text) return '';
  return text
    .split('\n')
    // Remove table border lines (starting with border characters) but keep those starting with content bars
    .filter(l => !/^[\s]*[┏┗┡┘└├┤┬┴┼─━═╔╗╚╝╠╣╦╩╬┌┐┣╋┫]/.test(l))
    .join('\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

/**
 * Extracts key-value pairs from ASCII tables.
 * @param {string} text
 * @returns {Object}
 */
function extractTableValues(text) {
  if (!text) return {};
  const result = {};
  text.split('\n').forEach(line => {
    const cells = line.split('│').map(s => s.trim()).filter(Boolean);
    if (cells.length === 2 && !/^[━─═]+$/.test(cells[0])) {
      result[cells[0].toLowerCase()] = cells[1];
    }
  });
  return result;
}

/**
 * Cleans the output of a block: removes ASCII tables, system headers, and excessive empty lines.
 * @param {string} raw
 * @returns {string}
 */
function cleanOutput(raw) {
  if (!raw) return '';
  return raw
    .split('\n')
    // Remove table border lines and lines with only spaces
    .filter(l => !/^[\s]*[┏┗┡┘└├┤┬┴┼─━═╔╗╚╝╠╣╦╩╬═║┌┐┣╋┫]/.test(l))
    // Remove CLI system lines (Continuing conversation, Resumed conversation, Started:)
    .filter(l => !/^(Continuing conversation|Resumed conversation|Started:|Matched:)/i.test(l.trim()))
    .join('\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    stripCliTables,
    extractTableValues,
    cleanOutput
  };
}
