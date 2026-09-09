/* ═══════════════════════════════════════════════════════════════════
   FRAME — «Світло і простір». Логіка макета без бібліотек.

   Файл написано так, щоб перехід до Vue був перекладом, а не
   переписуванням. Розділи нижче названі тими поняттями, якими
   оперує компонент:

     дані          → props
     стан          → ref / reactive
     похідні дані  → computed
     рендер        → шаблон
     дії           → методи та emits

   Головна відмінність, яку варто побачити студентові: тут кожна
   зміна стану вимагає ручного оновлення розмітки (renderPhoto,
   renderInfo, renderNav). Забути один виклик — і на екрані опис
   одного кадру поруч із фотографією іншого. Реактивність Vue
   прибирає саме цей клас помилок: змінюється стан, розмітка
   доганяє сама.
   ═══════════════════════════════════════════════════════════════════ */

'use strict'

/* ── Дані ───────────────────────────────────────────────────────────
   У Vue це масив в App.vue, який передається донизу:
   <Gallery :images="images" />. Галерея не ходить по дані сама —
   інакше її не можна показати двічі з різними колекціями.
   ────────────────────────────────────────────────────────────────── */

const images = [
  {
    title: 'Геометрія тиші',
    description: 'Чисті лінії, відкрите небо та ритм архітектури. Простір, у якому головною деталлю стає світло.',
    tag: 'Архітектура',
    photo: 'photo-1487958449943-2429e8be8625',
    alt: 'Світла сучасна будівля з геометричними фасадами'
  },
  {
    title: 'Місто вгору',
    description: 'Погляд поміж будівлями відкриває інше місто. Вертикальні лінії збирають небо в окремий кадр.',
    tag: 'Перспектива',
    photo: 'photo-1486406146926-c627a92ad1ab',
    alt: 'Висотні будівлі, зняті знизу на тлі неба'
  },
  {
    title: 'За горизонтом',
    description: 'Гірський ландшафт розкладається на плани. Далечінь поступово розчиняється у світлі.',
    tag: 'Ландшафт',
    photo: 'photo-1464822759023-fed622ff2c3b',
    alt: 'Скелясті гірські вершини'
  },
  {
    title: 'Зелена пауза',
    description: 'Ліс створює власний ритм. Поміж деревами простір стає тихішим, а відтінки — глибшими.',
    tag: 'Природа',
    photo: 'photo-1448375240586-882707db888b',
    alt: 'Ліс із високими деревами'
  },
  {
    title: 'Відкрита вода',
    description: 'Вода поєднує рух і спокій. Відбиття та берег утворюють просту, врівноважену композицію.',
    tag: 'Відображення',
    photo: 'photo-1470770841072-f978cf4d019e',
    alt: 'Озеро в гірському ландшафті'
  },
  {
    title: 'Тепло землі',
    description: 'Плавні обриси піску змінюють відчуття масштабу. Світло перетворює поверхню на абстрактний малюнок.',
    tag: 'Фактура',
    photo: 'photo-1509316785289-025f5b846b35',
    alt: 'Піщані дюни пустелі'
  }
]

/* ── Гачки розмітки ─────────────────────────────────────────────────
   Пошук вузлів зібрано в одне місце: далі по файлу немає жодного
   querySelector. Шукаємо за data-role, а не за класами БЕМ —
   класи належать дизайнерові, data-role програмістові, і кожен
   може міняти своє, не ламаючи чуже.

   У Vue цей розділ зникає цілком: до DOM звертається шаблон.
   ────────────────────────────────────────────────────────────────── */

const dom = {
  gallery: document.querySelector('[data-role="gallery"]'),
  photo: document.querySelector('[data-role="photo"]'),
  image: document.querySelector('[data-role="image"]'),
  message: document.querySelector('[data-role="message"]'),
  number: document.querySelector('[data-role="number"]'),
  total: document.querySelector('[data-role="total"]'),
  title: document.querySelector('[data-role="title"]'),
  description: document.querySelector('[data-role="description"]'),
  tag: document.querySelector('[data-role="tag"]'),
  prev: document.querySelector('[data-role="prev"]'),
  next: document.querySelector('[data-role="next"]'),
  empty: document.querySelector('[data-role="empty"]')
}

/* ── Стан ───────────────────────────────────────────────────────────
   Єдина змінна величина сторінки. У Vue: const selectedIndex = ref(0)
   всередині Gallery — саме всередині, тому два екземпляри галереї
   мають незалежний стан.
   ────────────────────────────────────────────────────────────────── */

let selectedIndex = 0

/* ── Похідні дані ───────────────────────────────────────────────────
   У Vue це computed. Похідне значення ніколи не зберігають у стані:
   збережена копія рано чи пізно розійдеться з оригіналом.
   ────────────────────────────────────────────────────────────────── */

const currentImage = () => images[selectedIndex]
const isSingle = () => images.length < 2
const padded = (value) => String(value).padStart(2, '0')

/* ── Побудова адреси зображення ─────────────────────────────────────
   Ширина й висота задані явно: пропорція 3:2 збігається з width
   і height у розмітці, тому місце під фотографію займається одразу
   і сторінка не стрибає під час завантаження.
   ────────────────────────────────────────────────────────────────── */

const PHOTO_WIDTH = 1800
const PHOTO_HEIGHT = 1200

function photoUrl (image) {
  return 'https://images.unsplash.com/' + image.photo +
    '?auto=format&fit=crop&w=' + PHOTO_WIDTH + '&h=' + PHOTO_HEIGHT + '&q=85'
}

/* ── Рендер: блок .photo → GalleryImage ─────────────────────────────
   Компонент показує кадр і власний стан завантаження. Модифікатори
   .photo--loading і .photo--failed — це те, що у Vue стане
   :class="{ 'photo--loading': loading }".
   ────────────────────────────────────────────────────────────────── */

function renderPhoto (image) {
  dom.photo.classList.remove('photo--failed')
  dom.photo.classList.add('photo--loading')
  dom.message.hidden = true

  dom.image.src = photoUrl(image)
  dom.image.alt = image.alt

  // Кадр із кешу вже готовий на момент присвоєння: подія load
  // для нього не спрацює, тому перевіряємо стан явно.
  if (dom.image.complete && dom.image.naturalWidth > 0) onPhotoLoad()
}

// Обробник описує стан цілком, а не лише свою частину: успішне
// завантаження скасовує і очікування, і попередню помилку.
function onPhotoLoad () {
  dom.photo.classList.remove('photo--loading', 'photo--failed')
  dom.message.hidden = true
}

function onPhotoError () {
  dom.photo.classList.remove('photo--loading')
  dom.photo.classList.add('photo--failed')
  dom.message.hidden = false
}

/* ── Рендер: блок .frame-info → FrameInfo ───────────────────────────
   Чистий вивід: жодних рішень, лише показ переданого кадру.
   textContent, а не innerHTML: текст лишається текстом, розмітка
   з даних у сторінку не потрапляє.
   ────────────────────────────────────────────────────────────────── */

function renderInfo (image) {
  dom.number.textContent = padded(selectedIndex + 1)
  dom.total.textContent = padded(images.length)
  dom.title.textContent = image.title
  dom.description.textContent = image.description
  dom.tag.textContent = image.tag
}

/* ── Рендер: блок .gallery-nav → GalleryNavigation ──────────────────
   Єдиний кадр гортати нікуди — кнопки вимкнені. У Vue це prop
   disabled, обчислений галереєю: сама навігація про кількість
   кадрів не знає.
   ────────────────────────────────────────────────────────────────── */

function renderNav () {
  dom.prev.disabled = isSingle()
  dom.next.disabled = isSingle()
}

/* ── Дія: показати кадр ─────────────────────────────────────────────
   Залишок від ділення робить перегляд кільцевим: після останнього
   кадру відкривається перший, перед першим — останній.
   ────────────────────────────────────────────────────────────────── */

function show (index) {
  selectedIndex = (index + images.length) % images.length

  const image = currentImage()
  renderPhoto(image)
  renderInfo(image)
  renderNav()
  preloadNeighbours()
}

/* Сусідні кадри тихо вантажаться у фон, тому наступне натискання
   показує фотографію одразу. Об'єкт Image нікуди не додають:
   достатньо того, що браузер поклав відповідь у кеш. */
function preloadNeighbours () {
  if (isSingle()) return

  const around = [selectedIndex + 1, selectedIndex - 1]
  around.forEach((index) => {
    const image = images[(index + images.length) % images.length]
    new Image().src = photoUrl(image)
  })
}

/* ── Наміри користувача ─────────────────────────────────────────────
   У Vue ці два виклики стануть обробниками подій компонента:
   <GalleryNavigation @previous="show(selectedIndex - 1)" ... />.
   Кнопка повідомляє про намір, стан змінює галерея.
   ────────────────────────────────────────────────────────────────── */

function showPrevious () { show(selectedIndex - 1) }
function showNext () { show(selectedIndex + 1) }

/* ── Порожній стан ──────────────────────────────────────────────────
   Порожній масив — не виняткова ситуація, а звичайний вхід.
   ────────────────────────────────────────────────────────────────── */

function renderEmpty () {
  dom.gallery.hidden = true
  dom.empty.hidden = false
}

/* ── Запуск ─────────────────────────────────────────────────────────
   У Vue цього розділу немає: створення застосунку та прив'язка
   подій описані декларативно в шаблоні.
   ────────────────────────────────────────────────────────────────── */

function init () {
  if (images.length === 0) {
    renderEmpty()
    return
  }

  dom.image.addEventListener('load', onPhotoLoad)
  dom.image.addEventListener('error', onPhotoError)
  dom.prev.addEventListener('click', showPrevious)
  dom.next.addEventListener('click', showNext)

  // Гортання з клавіатури, поки фокус усередині галереї.
  // Кнопки лишаються основним способом: клавіші їх доповнюють,
  // а не замінюють.
  dom.gallery.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') { showPrevious(); event.preventDefault() }
    if (event.key === 'ArrowRight') { showNext(); event.preventDefault() }
  })

  show(0)
}

init()
