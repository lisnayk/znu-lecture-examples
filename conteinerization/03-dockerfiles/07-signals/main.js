// Обробники дають процесу PID 1 явну реакцію на сигнали завершення.
const timer = setInterval(() => {}, 1000)
for (const signal of ['SIGTERM', 'SIGINT']) {
  process.on(signal, () => {
    if (signal === 'SIGTERM' && process.env.IGNORE_TERM === '1') return
    clearInterval(timer)
    process.stdout.write(`${signal}: завершення роботи\n`, () => process.exit(0))
  })
}
console.log('READY')
