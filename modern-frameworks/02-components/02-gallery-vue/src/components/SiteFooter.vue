<script setup>
// ── SiteFooter ────────────────────────────────────────────────────
</script>

<template>
  <footer class="site-footer">
    <span class="site-footer__brand">FRAME / Світло у звичайному.</span>
    <span>Навчальний дизайн-макет · Фотографії: Unsplash · Потрібне підключення до мережі</span>
  </footer>
</template>

<style scoped lang="scss">
.site-footer {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  margin-top: 28px;
  padding-top: 17px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 9px;
  letter-spacing: 0.5px;

  @include phone {
    gap: 20px;
    line-height: 1.6;
  }
}

.site-footer__brand {
  color: var(--ink);
}
</style>
