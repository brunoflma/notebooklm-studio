const { esc } = (function() {
    function esc(s){
      if(!s)return '';
      return s.toString().replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
    }
    return { esc };
})();

function testEsc() {
    const cases = [
        { input: 'hello', expected: 'hello' },
        { input: '<b>world</b>', expected: '&lt;b&gt;world&lt;/b&gt;' },
        { input: 'Tom & Jerry', expected: 'Tom &amp; Jerry' },
        { input: 'Double "quote"', expected: 'Double &quot;quote&quot;' },
        { input: "Single 'quote'", expected: "Single &#39;quote&#39;" },
        { input: '<script>alert(1)</script>', expected: '&lt;script&gt;alert(1)&lt;/script&gt;' },
        { input: null, expected: '' },
        { input: undefined, expected: '' }
    ];

    let passed = 0;
    cases.forEach((c, i) => {
        const result = esc(c.input);
        if (result === c.expected) {
            console.log(`Test ${i + 1} passed`);
            passed++;
        } else {
            console.error(`Test ${i + 1} failed: expected "${c.expected}", got "${result}"`);
        }
    });

    console.log(`\nResults: ${passed}/${cases.length} tests passed`);
    if (passed !== cases.length) process.exit(1);
}

testEsc();
