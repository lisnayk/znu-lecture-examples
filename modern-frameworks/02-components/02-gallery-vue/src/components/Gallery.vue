<script setup>
// ── Gallery: єдиний власник стану ─────────────────────────────────
// Галерея вирішує, який кадр показано, і більше нічого не робить сама:
// показ кадру, підписи й кнопки віддано трьом дочірнім компонентам.
// Дані йдуть униз через props, наміри користувача повертаються вгору
// через події.
import { computed, ref, watch } from 'vue'
import GalleryImage from './GalleryImage.vue'
import FrameInfo from './FrameInfo.vue'
import GalleryNavigation from './GalleryNavigation.vue'

const props = defineProps({
  images: { type: Array, default: () => [] },
})

// Стан галереї — вибір користувача, і тільки він.
const selectedId = ref(null)

// Решта обчислюється. Похідне значення не зберігають у стані:
// збережена копія рано чи пізно розійдеться з оригіналом.
const selectedIndex = computed(() => {
  const index = props.images.findIndex((image) => image.id === selectedId.value)
  return index < 0 ? 0 : index
})
const selectedImage = computed(() => props.images[selectedIndex.value] ?? null)
const total = computed(() => props.images.length)
const isSingle = computed(() => total.value < 2)

// Залишок від ділення робить перегляд кільцевим: після останнього кадру
// відкривається перший, перед першим — останній.
function move (step) {
  if (!total.value) return
  const nextIndex = (selectedIndex.value + step + total.value) % total.value
  selectedId.value = props.images[nextIndex].id
}

// Сусідні кадри тихо вантажаться у фон, тому наступне натискання
// показує фотографію одразу. Об'єкт Image нікуди не додають:
// досить того, що браузер поклав відповідь у кеш.
function preloadNeighbours () {
  if (isSingle.value) return

  for (const step of [1, -1]) {
    const index = (selectedIndex.value + step + total.value) % total.value
    new Image().src = props.images[index].src
  }
}

// watch стежить за похідним значенням; immediate запускає його одразу
// після створення компонента, а не лише після першої зміни.
watch(selectedIndex, preloadNeighbours, { immediate: true })
</script>

<template>
  <!-- Гортання з клавіатури працює, поки фокус усередині галереї:
       подія кнопки спливає до секції. Клавіші доповнюють кнопки,
       а не замінюють їх. -->
  <section
    v-if="selectedImage"
    class="gallery"
    aria-label="Перегляд обраного кадру"
    @keydown.left.prevent="move(-1)"
    @keydown.right.prevent="move(1)"
  >
    <GalleryImage :image="selectedImage" />

    <div class="gallery__details">
      <FrameInfo
        :image="selectedImage"
        :position="selectedIndex + 1"
        :total="total"
      />
      <GalleryNavigation
        :disabled="isSingle"
        @previous="move(-1)"
        @next="move(1)"
      />
    </div>
  </section>

  <!-- Порожній масив — не виняткова ситуація, а звичайний вхід. -->
  <p v-else class="gallery-empty" role="status">
    У цій колекції поки немає кадрів.
  </p>
</template>

<style scoped lang="scss">
.gallery {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  min-height: 420px;
  overflow: hidden;
  border-radius: 5px;
  background: var(--surface);

  @include lap {
    grid-template-columns: minmax(0, 1fr) 240px;
    min-height: 360px;
  }

  @include phone {
    grid-template-columns: 1fr;
  }
}

.gallery__details {
  display: flex;
  flex-direction: column;
  padding: 28px;

  @include lap {
    padding: 24px;
  }

  @include phone {
    padding: 22px;
  }
}

.gallery-empty {
  margin: 20px 0 0;
  color: var(--muted);
  font-size: 13px;
}
</style>
