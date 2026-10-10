// List providers/options that fall back to logo.png and mappings that point to missing files.
// Usage: node scripts/check_logos.js   (run from the repo root)
const fs = require('fs');

const t = fs.readFileSync('templates/template.html', 'utf8');
const start = t.indexOf('function imageOf(');
let end = t.indexOf('{', start), depth = 0;
for (; end < t.length; end++) {
    if (t[end] === '{') depth++;
    if (t[end] === '}' && --depth === 0) break;
}
eval(t.slice(start, end + 1));

const pairs = new Map();
for (const f of ['running', 'agents', 'software-engineering'])
    for (const o of JSON.parse(fs.readFileSync(`data/${f}.json`)).options) pairs.set(`${o.provider}|${o.name}`, f);
for (const m of JSON.parse(fs.readFileSync('data/tools-timeline.json')).milestones) pairs.set(`${m.provider}|${m.name}`, 'timeline');

const missing = new Map(), broken = new Set();
for (const [key, file] of pairs) {
    const [provider, name] = key.split('|');
    const img = imageOf(provider, name);
    if (img === 'logo.png') {
        if (!missing.has(provider)) missing.set(provider, []);
        missing.get(provider).push(`${file}: ${name}`);
    } else if (!fs.existsSync(`docs/assets/${img}`)) broken.add(`${img} <- ${provider}`);
}
for (const l of JSON.parse(fs.readFileSync('data/data.json')).frontier_labs)
    if (!fs.existsSync(`docs/assets/${l.logo}`)) broken.add(`${l.logo} <- lab ${l.name}`);

for (const [provider, items] of missing) console.log(`${provider} :: ${[...new Set(items)].slice(0, 3).join('; ')}`);
console.log(`${missing.size} providers on default logo; broken: ${broken.size ? [...broken].join(', ') : 'none'}`);
