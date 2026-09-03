// Той самий інтерфейс, що й у решті прикладів, але оновлення DOM написані руками.
const state = { count: 0, entries: [] }

const app = document.querySelector('#app')
app.innerHTML = `
  <h1>Лічильник — без фреймворка</h1>
  <p class="count" id="count">0</p>
  <button id="add">Додати</button>
  <button id="clear">Очистити</button>
  <p id="total"></p>
  <ul id="list"></ul>`

const el = {
  count: app.querySelector('#count'),
  total: app.querySelector('#total'),
  list: app.querySelector('#list'),
}

// Стан і DOM синхронізуємо вручну.
function render() {
  el.count.textContent = state.count
  el.total.textContent = `Записів: ${state.entries.length}`
  el.list.innerHTML = state.entries.length
    ? state.entries.map((e) => `<li>${e}</li>`).join('')
    : '<li class="empty">поки порожньо</li>'
}

app.querySelector('#add').addEventListener('click', () => {
  state.count += 1
  const time = new Date().toLocaleTimeString('uk-UA')
  state.entries.unshift(`Запис ${state.count} о ${time}`)
  render()
})

app.querySelector('#clear').addEventListener('click', () => {
  state.count = 0
  state.entries = []
  render()
})

render()
