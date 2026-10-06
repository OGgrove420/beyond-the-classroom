// check whether jsdom exists on this machine
try { require.resolve('jsdom'); console.log('jsdom ok'); }
catch (e) { console.log('no jsdom'); }
try { require.resolve('linkedom'); console.log('linkedom ok'); }
catch (e) { console.log('no linkedom'); }
console.log('node', process.version);
