// Навчальний HTTP-сервер без зовнішніх залежностей: усе потрібне є в Node.js.
// Так образ збирається без npm install, і приклад не залежить від стану мережі.
const http = require('node:http')
const os = require('node:os')

const port = Number(process.env.PORT || 3000)
const title = process.env.APP_TITLE || 'Образ зібрано з Dockerfile'

const server = http.createServer((req, res) => {
  if (req.url === '/healthz') {
    res.writeHead(200, { 'Content-Type': 'application/json' })
    res.end(JSON.stringify({ status: 'ok' }))
    return
  }
  if (req.url !== '/') {
    res.writeHead(404, { 'Content-Type': 'application/json' })
    res.end(JSON.stringify({ error: 'not found' }))
    return
  }
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' })
  res.end(`<!doctype html>
<html lang="uk">
<head><meta charset="utf-8"><title>${title}</title></head>
<body>
<h1>${title}</h1>
<p>Вузол: ${os.hostname()}</p>
<p>Node.js: ${process.version}</p>
<p>Користувач процесу: uid=${process.getuid()}</p>
<p>Робочий каталог: ${process.cwd()}</p>
</body>
</html>
`)
})

server.listen(port, '0.0.0.0', () => {
  console.log(`Слухаю 0.0.0.0:${port}`)
})
