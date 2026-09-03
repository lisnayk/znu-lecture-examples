<script>
  let count = $state(0)
  let entries = $state([])
  let total = $derived(`Записів: ${entries.length}`)

  function add() {
    count += 1
    const time = new Date().toLocaleTimeString('uk-UA')
    entries = [`Запис ${count} о ${time}`, ...entries]
  }

  function clear() {
    count = 0
    entries = []
  }
</script>

<h1>Лічильник — Svelte</h1>
<p class="count">{count}</p>
<button onclick={add}>Додати</button>
<button onclick={clear}>Очистити</button>
<p>{total}</p>
<ul>
  {#each entries as e (e)}
    <li>{e}</li>
  {/each}
  {#if entries.length === 0}
    <li class="empty">поки порожньо</li>
  {/if}
</ul>
