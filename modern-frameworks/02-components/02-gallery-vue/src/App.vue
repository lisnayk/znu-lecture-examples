<script setup>
// ── App: збирає сторінку й володіє даними ─────────────────────────
// Кореневий компонент відповідає за дві речі: звідки беруться кадри
// і в якому порядку стоять частини сторінки. Логіки галереї тут
// немає — інакше другу галерею на сторінку не поставити.
import SiteHeader from './components/SiteHeader.vue'
import SiteIntro from './components/SiteIntro.vue'
import Gallery from './components/Gallery.vue'
import SiteFooter from './components/SiteFooter.vue'
import { images } from './data/images.js'
</script>

<template>
  <main class="page">
    <SiteHeader />
    <SiteIntro />

    <!-- Кадри передано через props. Галерея не імпортує дані сама,
         тому поруч можна поставити <Gallery :images="інша колекція" />
         і два перегляди працюватимуть незалежно. -->
    <Gallery :images="images" />

    <SiteFooter />
  </main>
</template>

<style scoped lang="scss">
.page {
  max-width: $content-max;
  margin: auto;
  padding: 30px 56px 24px;

  @include lap {
    padding: 24px;
  }

  @include phone {
    padding: 20px 17px;
  }
}
</style>
