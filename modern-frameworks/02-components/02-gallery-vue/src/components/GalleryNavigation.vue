<script setup>
// ── GalleryNavigation: кнопки гортання ────────────────────────────
// Компонент не змінює вибір і навіть не знає про нього. Він
// повідомляє про намір користувача, рішення ухвалює галерея.
// Тому його можна поставити під фотографією, збоку або в шапці,
// нічого не переписуючи.
defineProps({
  disabled: { type: Boolean, default: false },
})

// Перелік подій оголошено явно: це такий самий контракт компонента,
// як і props, і його видно з першого рядка.
const emit = defineEmits(['previous', 'next'])
</script>

<template>
  <div class="gallery-nav">
    <div class="gallery-nav__rule" />

    <div class="gallery-nav__controls">
      <button
        class="gallery-nav__button"
        type="button"
        :disabled="disabled"
        aria-label="Попередній кадр"
        @click="emit('previous')"
      >
        <svg
          class="gallery-nav__icon"
          width="20" height="20" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" stroke-width="1.7"
          stroke-linecap="round" stroke-linejoin="round"
          aria-hidden="true" focusable="false"
        >
          <path d="M14 6l-6 6 6 6" />
        </svg>
      </button>

      <small class="gallery-nav__hint">Знайдіть свій ракурс</small>

      <button
        class="gallery-nav__button"
        type="button"
        :disabled="disabled"
        aria-label="Наступний кадр"
        @click="emit('next')"
      >
        <svg
          class="gallery-nav__icon"
          width="20" height="20" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" stroke-width="1.7"
          stroke-linecap="round" stroke-linejoin="round"
          aria-hidden="true" focusable="false"
        >
          <path d="M10 6l6 6-6 6" />
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.gallery-nav {
  // Навігація притискається до низу колонки опису.
  margin-top: auto;
  padding-top: 25px;

  @include phone {
    padding-top: 19px;
  }
}

.gallery-nav__rule {
  height: 1px;
  margin-bottom: 17px;
  background: var(--rule);
}

.gallery-nav__controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.gallery-nav__button {
  @include focus-ring;

  display: grid;
  place-items: center;
  // 44 × 44 — найменша ціль, у яку впевнено влучає палець.
  width: 44px;
  height: 44px;
  border: 1px solid var(--control-border);
  border-radius: 6px;
  background: transparent;
  color: var(--focus);
  font: inherit;
  cursor: pointer;
  touch-action: manipulation;
  transition: background-color 140ms ease, border-color 140ms ease;

  &:hover {
    background: var(--control-hover);
    border-color: var(--focus);
    color: var(--ink);
  }

  &:active {
    background: var(--control-active);
  }

  &:disabled {
    opacity: 0.4;
    cursor: default;
  }
}

// Клік по значку має потрапляти в кнопку, а не в <svg>.
.gallery-nav__icon {
  pointer-events: none;
}

.gallery-nav__hint {
  @include micro(9px);

  color: var(--muted);
}
</style>
