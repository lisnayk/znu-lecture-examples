import { useState } from 'react'

export default function App() {
  const [count, setCount] = useState(0)
  const [entries, setEntries] = useState([])
  const total = `Записів: ${entries.length}`

  function add() {
    const next = count + 1
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
      <h1>Лічильник — React</h1>
      <p className="count">{count}</p>
      <button onClick={add}>Додати</button>
      <button onClick={clear}>Очистити</button>
      <p>{total}</p>
      <ul>
        {entries.map((e) => <li key={e}>{e}</li>)}
        {entries.length === 0 && (
          <li className="empty">поки порожньо</li>
        )}
      </ul>
    </>
  )
}
