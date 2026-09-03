<script setup>
import { ref, computed } from 'vue'

const count = ref(0)
const entries = ref([])
const total = computed(() => `Записів: ${entries.value.length}`)

function add() {
  count.value += 1
  const time = new Date().toLocaleTimeString('uk-UA')
  entries.value.unshift(`Запис ${count.value} о ${time}`)
}

function clear() {
  count.value = 0
  entries.value = []
}
</script>

<template>
  <h1>Лічильник — Vue</h1>
  <p class="count">{{ count }}</p>
  <button @click="add">Додати</button>
  <button @click="clear">Очистити</button>
  <p>{{ total }}</p>
  <ul>
    <li v-for="e in entries" :key="e">{{ e }}</li>
    <li v-if="!entries.length" class="empty">поки порожньо</li>
  </ul>
</template>
