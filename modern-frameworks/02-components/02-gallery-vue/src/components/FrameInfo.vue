<script setup>
// ── FrameInfo: підписи до кадру ───────────────────────────────────
// Компонент без власного стану: те, що прийшло у props, і визначає
// вигляд повністю. Такі компоненти найлегше перевіряти й найважче
// зламати — у них просто немає де накопичитися розбіжності.
import { computed } from 'vue'
import TagList from './TagList.vue'

const props = defineProps({
  image: { type: Object, required: true },
  position: { type: Number, required: true },
  total: { type: Number, required: true },
})

// Форматування — справа того, хто показує. Галерея передає числа,
// а не рядки: інакше вона мусила б знати, як вони виглядають.
const padded = (value) => String(value).padStart(2, '0')
const positionLabel = computed(() => padded(props.position))
const totalLabel = computed(() => padded(props.total))

const tags = computed(() => [props.image.tag, 'Колекція 001'])
</script>

<template>
  <article class="frame-info">
    <p class="frame-info__counter">
      <strong class="frame-info__number">{{ positionLabel }}</strong>
      <span class="frame-info__total">/ {{ totalLabel }}</span>
    </p>

    <!-- Заголовок і опис змінюються без перезавантаження сторінки,
         тож читач екрана має почути новий текст. -->
    <div aria-live="polite" aria-atomic="true">
      <h2 class="frame-info__title">{{ image.title }}</h2>
      <p class="frame-info__text">{{ image.description }}</p>
    </div>

    <TagList :items="tags" />
  </article>
</template>

<style scoped lang="scss">
.frame-info {
  margin: 0;
}

.frame-info__counter {
  display: flex;
  align-items: baseline;
  gap: 9px;
  margin: 0;
  // Цифри однакової ширини: без цього номер сіпається при гортанні.
  font-variant-numeric: tabular-nums;
}

.frame-info__number {
  font-family: $font-display;
  font-size: 48px;
  font-weight: 400;
  letter-spacing: -3px;

  @include phone {
    font-size: 33px;
  }
}

.frame-info__total {
  color: var(--muted);
  font-size: 12px;
}

.frame-info__title {
  margin: 37px 0 16px;
  font-family: $font-display;
  font-size: 36px;
  font-weight: 400;
  line-height: 1.05;
  letter-spacing: -1.3px;
  text-wrap: balance;

  @include lap {
    font-size: 30px;
  }

  @include phone {
    margin: 13px 0 12px;
  }
}

.frame-info__text {
  margin: 0;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.8;
}
</style>
