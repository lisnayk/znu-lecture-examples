<script setup>
// ── TagList: перелік підписів ─────────────────────────────────────
// Найдрібніший компонент набору. Виділений не заради повторного
// використання, а тому, що це самостійний блок розмітки: він не
// знає ні про галерею, ні про кадр — лише про список рядків.
defineProps({
  items: { type: Array, default: () => [] },
})
</script>

<template>
  <!-- Перелік рівнозначних підписів — це список, а не набір <span>. -->
  <ul v-if="items.length" class="tag-list">
    <li v-for="item in items" :key="item" class="tag-list__item">
      {{ item }}
    </li>
  </ul>
</template>

<style scoped lang="scss">
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 20px 0 0;
  padding: 0;
  list-style: none;
}

.tag-list__item {
  @include micro(9px, 1px);

  padding: 6px 8px;
  border-radius: 20px;
  background: var(--tag-bg);
  color: var(--tag-ink);
}
</style>
