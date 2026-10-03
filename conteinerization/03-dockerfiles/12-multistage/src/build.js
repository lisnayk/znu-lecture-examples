// Навчальний генератор статики: перетворює JSON у HTML без зовнішніх пакетів.
const fs = require('node:fs')
const path = require('node:path')

const data = JSON.parse(fs.readFileSync(path.join(__dirname, 'content.json'), 'utf8'))
const out = path.join(process.cwd(), 'dist')
fs.mkdirSync(out, { recursive: true })

const items = data.sections.map((s) => `  <li><b>${s.title}</b> — ${s.text}</li>`).join('\n')
fs.writeFileSync(path.join(out, 'index.html'), `<!doctype html>
<html lang="uk">
<head><meta charset="utf-8"><title>${data.title}</title></head>
<body>
<h1>${data.title}</h1>
<ul>
${items}
</ul>
<p>Зібрано на етапі build, віддається з етапу prod.</p>
</body>
</html>
`)
console.log('dist/index.html створено')
