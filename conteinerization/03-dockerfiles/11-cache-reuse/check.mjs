import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import assert from 'node:assert/strict'
import {spawnSync} from 'node:child_process'
const dir=import.meta.dirname
const context=fs.mkdtempSync(path.join(os.tmpdir(),'lecture3-cache-'))
for(const file of ['Dockerfile','package.json','package-lock.json','app.js']) fs.copyFileSync(path.join(dir,file),path.join(context,file))
const baselinePkg=JSON.parse(fs.readFileSync(path.join(context,'package.json'),'utf8'))
baselinePkg.description=path.basename(context)+'-base'
fs.writeFileSync(path.join(context,'package.json'),JSON.stringify(baselinePkg))
const image='lecture3-cache:review'
function build(name,extra=[]) {
 const run=spawnSync('docker',['build','--progress=plain',...extra,'-t',image,context],{encoding:'utf8'})
 const log=run.stdout+run.stderr
 fs.writeFileSync(path.join(context, name+'.log'),log)
 assert.equal(run.status,0,log)
 return log
}
function cached(log,command,want) {
 const escaped=command.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')
 const m=log.match(new RegExp('^#(\\d+) \\[[^\\n]*\\] '+escaped+'$','m'))
 assert.ok(m,'Немає кроку '+command+'\n'+log)
 assert.equal(log.includes('#'+m[1]+' CACHED'),want,command+'\n'+log)
}
const steps=['COPY package*.json ./','RUN npm ci --ignore-scripts','COPY app.js ./']
build('initial',['--no-cache'])
const same=build('unchanged')
steps.forEach(s=>cached(same,s,true))
console.log('PASS без змін: усі три кроки CACHED')
fs.writeFileSync(path.join(context,'app.js'),"console.log('Версія 2')\n")
const app=build('code-changed')
steps.forEach((s,i)=>cached(app,s,i<2))
console.log('PASS зміна коду: залежності CACHED, COPY app.js перебудовано')
const pkg=JSON.parse(fs.readFileSync(path.join(context,'package.json'),'utf8'))
pkg.description=path.basename(context)+'-changed'
fs.writeFileSync(path.join(context,'package.json'),JSON.stringify(pkg))
const deps=build('package-changed')
steps.forEach(s=>cached(deps,s,false))
console.log('PASS зміна package.json: усі три кроки перебудовано')
const run=spawnSync('docker',['run','--rm',image],{encoding:'utf8'})
assert.equal(run.status,0,run.stderr)
assert.equal(run.stdout.trim(),'Версія 2')
console.log('PASS образ запускається та друкує Версія 2')
console.error('Логи перевірки збережено у '+context)
