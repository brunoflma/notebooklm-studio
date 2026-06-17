const esc = (s) => s ? String(s).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"}[m])) : '';

const tests = [
  { input: '<script>alert(1)</script>', expected: '&lt;script&gt;alert(1)&lt;/script&gt;' },
  { input: '"><img src=x onerror=alert(1)>', expected: '&quot;&gt;&lt;img src=x onerror=alert(1)&gt;' },
  { input: "'-alert(1)-'", expected: '&#39;-alert(1)-&#39;' },
  { input: 'A & B', expected: 'A &amp; B' },
  { input: 'Normal text', expected: 'Normal text' },
  { input: '', expected: '' },
  { input: null, expected: '' },
  { input: undefined, expected: '' }
];

let failed = 0;
tests.forEach((t, i) => {
  const result = esc(t.input);
  if (result !== t.expected) {
    console.error(`Test ${i} failed: expected "${t.expected}", got "${result}"`);
    failed++;
  } else {
    console.log(`Test ${i} passed`);
  }
});

if (failed > 0) {
  process.exit(1);
} else {
  console.log('All security tests passed!');
}
