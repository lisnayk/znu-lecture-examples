import { createMemo, createSignal, For, Show } from 'solid-js'

export default function App() {
  const [count, setCount] = createSignal(0)
  const [entries, setEntries] = createSignal([])
  const total = createMemo(() => `Записів: ${entries().length}`)

  function add() {
    const next = count() + 1
    setCount(next)
    setEntries((list) => [
      `Запис ${next} о ${new Date().toLocaleTimeString('uk-UA')}`,
      ...list,
    ])
  }

  function clear() {
    setCount(0)
    setEntries([])
  }

  return (
    <>
      <h1>Лічильник — Solid</h1>
      <p class="count">{count()}</p>
      <button onClick={add}>Додати</button>
      <button onClick={clear}>Очистити</button>
      <p>{total()}</p>
      <ul>
        <For each={entries()}>{(entry) => <li>{entry}</li>}</For>
        <Show when={entries().length === 0}>
          <li class="empty">поки порожньо</li>
        </Show>
      </ul>
    </>
  )
}
