<template>
  <main>
    <h1>Legacy Vue 2</h1>
    <p>Версія Vue {{ version }}</p>
    <button type="button" @click="count += 1">Натискань {{ count }}</button>
  </main>
</template>

<script>
import Vue from 'vue'

export default {
  data() {
    return { version: Vue.version, count: 0 }
  },
}
</script>

<style scoped>
main {
  max-width: 34rem;
  margin: 12vh auto;
  padding: 1.5rem;
  font: 1rem/1.5 system-ui, sans-serif;
  color: #14161b;
}
button {
  padding: 0.5rem 1rem;
  font: inherit;
}
</style>
