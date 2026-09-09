<script setup>
// ── SiteHeader ────────────────────────────────────────────────────
// Постійна частина сторінки. Компонент без props і без стану
// виділяють не заради повторного використання, а щоб App.vue
// лишався оглядовим: із нього має бути видно будову сторінки,
// а не її подробиці.
import BaseBadge from './BaseBadge.vue'
</script>

<template>
  <header class="site-header">
    <div class="site-header__brand">
      FRAME<i class="site-header__mark" aria-hidden="true" />
    </div>

    <div class="site-header__meta">
      <span class="site-header__note">Невелика колекція. Інший погляд.</span>
      <BaseBadge text="Візуальний архів / 001" />
    </div>
  </header>
</template>

<style scoped lang="scss">
.site-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 23px;
  border-bottom: 1px solid var(--line);
}

.site-header__brand {
  font-size: 27px;
  font-weight: 900;
  letter-spacing: -2px;

  @include phone {
    font-size: 24px;
  }
}

.site-header__mark {
  display: inline-block;
  width: 17px;
  height: 17px;
  margin-left: 7px;
  background: var(--ink);
  transform: rotate(-15deg);
}

.site-header__meta {
  display: flex;
  gap: 38px;
  align-items: center;
}

.site-header__note {
  @include micro;

  // На вузькому екрані другорядний підпис зникає першим.
  @include lap {
    display: none;
  }
}
</style>
