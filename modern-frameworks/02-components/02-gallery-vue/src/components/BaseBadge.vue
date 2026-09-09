<script setup>
// ── BaseBadge: позначка з крапкою ─────────────────────────────────
// Блок, який нічого не знає про своє оточення: приймає текст і
// показує його. Префікс Base — домовленість про компоненти,
// що не мають власної логіки й не залежать від застосунку.
defineProps({
  text: { type: String, required: true },
})
</script>

<template>
  <span class="badge">
    <span class="badge__dot" aria-hidden="true" />{{ text }}
  </span>
</template>

<style scoped lang="scss">
.badge {
  @include micro(10px, 1px);

  border: 1px solid var(--line);
  border-radius: 30px;
  padding: 10px 15px;

  @include phone {
    font-size: 8px;
  }
}

.badge__dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  margin-right: 7px;
  border-radius: 50%;
  background: var(--signal);
}
</style>
