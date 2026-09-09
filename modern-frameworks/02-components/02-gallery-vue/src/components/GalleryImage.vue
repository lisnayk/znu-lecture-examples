<script setup>
// ── GalleryImage: показ одного кадру ──────────────────────────────
// Компонент нічого не вирішує щодо колекції: він отримує кадр і
// показує його. Власний стан у нього все ж є — стан завантаження
// фотографії. Це його внутрішня справа, галереї про неї знати не треба.
import { ref, watch } from 'vue'
import { PHOTO_HEIGHT, PHOTO_WIDTH } from '../data/images.js'

const props = defineProps({
  image: { type: Object, required: true },
})

// 'loading' → 'ready' | 'failed'
const status = ref('loading')

// Зміна props — теж подія, на яку компонент має відповісти:
// новий кадр повертає стан до очікування.
watch(() => props.image.id, () => {
  status.value = 'loading'
})
</script>

<template>
  <div
    class="photo"
    :class="{
      'photo--loading': status === 'loading',
      'photo--failed': status === 'failed',
    }"
  >
    <!-- width і height задають пропорцію заздалегідь і прибирають
         стрибок розкладки. fetchpriority підказує браузерові, що це
         головне зображення сторінки. -->
    <img
      class="photo__image"
      :src="image.src"
      :alt="image.alt"
      :width="PHOTO_WIDTH"
      :height="PHOTO_HEIGHT"
      fetchpriority="high"
      @load="status = 'ready'"
      @error="status = 'failed'"
    >

    <span class="photo__mark">Вибраний кадр</span>
    <span class="photo__label" aria-hidden="true">FRAME — A STUDY OF LIGHT &amp; SPACE</span>

    <p v-if="status === 'failed'" class="photo__message" role="status">
      Кадр не завантажився. Перевірте підключення до мережі.
    </p>
  </div>
</template>

<style scoped lang="scss">
.photo {
  position: relative;
  min-width: 0;
  overflow: hidden;
  background: var(--photo-bg);

  // Від планшета й ширше фотографія веде висоту сама, без жорсткої пропорції.
  @include from-tablet {
    min-height: clamp(360px, 34vw, 560px);
  }

  @include phone {
    aspect-ratio: 1.25;
  }
}

.photo__image {
  position: absolute;
  inset: 0;
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 220ms ease;
}

// Затемнення нижньої частини, щоб білий підпис лишався читабельним
// на будь-якій фотографії.
.photo::after {
  content: '';
  position: absolute;
  inset: 50% 0 0;
  background: linear-gradient(transparent, #0004);
  pointer-events: none;
}

// Стан компонента — модифікатор блоку. Поки кадр вантажиться,
// попередній лишається видимим приглушено: порожній прямокутник
// читається як помилка, приглушений — як очікування.
.photo--loading .photo__image {
  opacity: 0.45;
}

.photo--failed {
  .photo__image {
    opacity: 0;
  }

  &::after {
    opacity: 0;
  }
}

.photo__mark {
  @include micro(9px, 1.6px);

  position: absolute;
  top: 21px;
  left: 23px;
  padding: 9px 12px;
  border-radius: 30px;
  background: color-mix(in srgb, var(--paper) 93%, transparent);
}

.photo__label {
  @include micro;

  position: absolute;
  bottom: 22px;
  left: 24px;
  z-index: 1;
  color: #fff;

  @include phone {
    font-size: 8px;
  }
}

.photo__message {
  position: absolute;
  inset: auto 24px 24px;
  z-index: 1;
  margin: 0;
  padding: 12px 14px;
  border-radius: 4px;
  background: color-mix(in srgb, var(--paper) 93%, transparent);
  color: var(--ink);
  font-size: 12px;
  line-height: 1.5;
}
</style>
