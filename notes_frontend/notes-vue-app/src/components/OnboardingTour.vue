<template>
  <Teleport to="body">
    <!-- Затемнение фона с "дыркой" вокруг активного элемента -->
    <div v-if="isVisible" class="tour-overlay" @click.self="skipTour">
      <!-- Spotlight — подсветка элемента -->
      <div
        v-if="spotlightStyle"
        class="tour-spotlight"
        :style="spotlightStyle"
      ></div>
 
      <!-- Карточка подсказки -->
      <div class="tour-card" :style="cardStyle" @click.stop>
        <!-- Прогресс -->
        <div class="tour-progress">
          <div
            v-for="i in steps.length"
            :key="i"
            class="tour-dot"
            :class="{ active: i - 1 === currentStep, done: i - 1 < currentStep }"
            @click="goToStep(i - 1)"
          ></div>
        </div>

        <!-- Иконка шага -->
        <div class="tour-step-icon">{{ steps[currentStep].icon }}</div>

        <!-- Текст -->
        <h3 class="tour-title">{{ steps[currentStep].title }}</h3>
        <p class="tour-text">{{ steps[currentStep].text }}</p>

        <!-- Кнопки -->
        <div class="tour-actions">
          <button class="tour-skip" @click="skipTour">Пропустить</button>
          <div class="tour-nav">
            <button
              v-if="currentStep > 0"
              class="tour-btn tour-btn-prev"
              @click="prevStep"
            >← Назад</button>
            <button
              class="tour-btn tour-btn-next"
              @click="nextStep"
            >
              {{ currentStep === steps.length - 1 ? '🎉 Готово!' : 'Далее →' }}
            </button>
          </div>
        </div>

        <!-- Счётчик -->
        <div class="tour-counter">{{ currentStep + 1 }} / {{ steps.length }}</div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'complete'])

const STORAGE_KEY = 'tour_completed'

const isVisible = ref(false)
const currentStep = ref(0)
const spotlightRect = ref(null)
const windowSize = ref({ w: window.innerWidth, h: window.innerHeight })

// Шаги тура — selector указывает на DOM-элемент для подсветки
const steps = [
  {
    icon: '💭',
    title: 'Добро пожаловать в Копилку идей!',
    text: 'Это твоё личное пространство для хранения идей, заметок и чеклистов. Давай быстро покажу, что тут есть.',
    selector: '.nav-brand',
    position: 'bottom',
  },
  {
    icon: '✨',
    title: 'Создание новой идеи',
    text: 'Нажми «+ Новая идея», чтобы записать мысль, добавить теги и прикрепить файлы. Идеи никуда не денутся!',
    selector: '.nav-link[href="/create"]',
    position: 'bottom',
  },
  {
    icon: '🏷️',
    title: 'Теги для навигации',
    text: 'Теги помогают быстро находить нужные идеи. Можно фильтровать сразу по нескольким тегам — режим «И» или «ИЛИ».',
    selector: '.tags-section-inline',
    position: 'right',
  },
  {
    icon: '📋',
    title: 'Чеклист дел',
    text: 'Справа — твой чеклист. Генерируй списки дел по категориям, отмечай выполненное. Нажми «Чеклист» в меню.',
    selector: '.checklist-preview',
    position: 'left',
  },
  {
    icon: '💡',
    title: 'Идея дня',
    text: 'Каждый день — новая идея для вдохновения. Пометь заметку как «Кандидат для идеи дня», и она попадёт в ротацию.',
    selector: '.idea-section',
    position: 'right',
  },
  {
    icon: '🎯',
    title: 'Всё готово!',
    text: 'Ты знаешь всё необходимое. Начни с создания первой идеи — и копилка заработает. Удачи!',
    selector: null,
    position: 'center',
  },
]

// Вычисляем стиль spotlight
const spotlightStyle = computed(() => {
  if (!spotlightRect.value) return null
  const { top, left, width, height } = spotlightRect.value
  const pad = 10
  return {
    top: `${top - pad}px`,
    left: `${left - pad}px`,
    width: `${width + pad * 2}px`,
    height: `${height + pad * 2}px`,
  }
})

// Вычисляем позицию карточки относительно подсвеченного элемента
const cardStyle = computed(() => {
  const step = steps[currentStep.value]
  const isMobile = windowSize.value.w <= 480

  // На мобиле всегда снизу по центру — CSS переопределит позицию
  if (isMobile) {
    return { position: 'fixed' }
  }

  if (!spotlightRect.value || step.position === 'center') {
    return {
      position: 'fixed',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
    }
  }

  const { top, left, width, height } = spotlightRect.value
  const cardW = 320
  const cardH = 260
  const pad = 20
  const { w, h } = windowSize.value

  let style = { position: 'fixed', width: cardW + 'px' }

  if (step.position === 'bottom') {
    let t = top + height + pad + 10
    let l = left + width / 2 - cardW / 2
    l = Math.max(16, Math.min(l, w - cardW - 16))
    if (t + cardH > h - 16) t = top - cardH - pad
    style.top = `${t}px`
    style.left = `${l}px`
  } else if (step.position === 'right') {
    let l = left + width + pad + 10
    let t = top + height / 2 - cardH / 2
    t = Math.max(16, Math.min(t, h - cardH - 16))
    if (l + cardW > w - 16) l = left - cardW - pad
    style.left = `${l}px`
    style.top = `${t}px`
  } else if (step.position === 'left') {
    let l = left - cardW - pad - 10
    let t = top + height / 2 - cardH / 2
    t = Math.max(16, Math.min(t, h - cardH - 16))
    if (l < 16) l = left + width + pad
    style.left = `${l}px`
    style.top = `${t}px`
  }

  return style
})

// Находим DOM-элемент и считаем его координаты
const updateSpotlight = async () => {
  await nextTick()
  const step = steps[currentStep.value]
  if (!step.selector) {
    spotlightRect.value = null
    return
  }
  const el = document.querySelector(step.selector)
  if (!el) {
    spotlightRect.value = null
    return
  }
  const rect = el.getBoundingClientRect()
  spotlightRect.value = {
    top: rect.top,
    left: rect.left,
    width: rect.width,
    height: rect.height,
  }
  // Скроллим к элементу если нужно
  el.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
}

const onResize = () => {
  windowSize.value = { w: window.innerWidth, h: window.innerHeight }
  updateSpotlight()
}

const goToStep = (index) => {
  if (index < 0 || index >= steps.length) return
  currentStep.value = index
  updateSpotlight()
}

const nextStep = () => {
  if (currentStep.value < steps.length - 1) {
    currentStep.value++
    updateSpotlight()
  } else {
    completeTour()
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
    updateSpotlight()
  }
}

const skipTour = () => {
  completeTour()
}

const completeTour = () => {
  localStorage.setItem(STORAGE_KEY, 'true')
  isVisible.value = false
  currentStep.value = 0
  spotlightRect.value = null
  emit('update:modelValue', false)
  emit('complete')
}

// Запуск тура
const startTour = async () => {
  currentStep.value = 0
  isVisible.value = true
  await nextTick()
  updateSpotlight()
}

// Следим за пропом
watch(() => props.modelValue, (val) => {
  if (val) startTour()
  else if (isVisible.value) completeTour()
})
 
// Первый запуск — если тур не пройден
onMounted(() => {
  window.addEventListener('resize', onResize)
  if (!localStorage.getItem(STORAGE_KEY) && props.modelValue) {
    startTour()
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
})

defineExpose({ startTour })
</script>

<style scoped>
/* Затемнённый оверлей */
.tour-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  pointer-events: all;
  /* Затемнение через box-shadow на spotlight */
  background: transparent;
}

/* Псевдо-spotlight: элемент с box-shadow создаёт "дырку" */
.tour-spotlight {
  position: fixed;
  border-radius: 12px;
  box-shadow:
    0 0 0 4px rgba(201, 169, 232, 0.6),
    0 0 0 9999px rgba(0, 0, 0, 0.55);
  pointer-events: none;
  z-index: 10000;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  animation: pulse-border 2s ease-in-out infinite;
}

@keyframes pulse-border {
  0%,
  100% {
    box-shadow:
      0 0 0 4px rgba(201, 169, 232, 0.6),
      0 0 0 9999px rgba(0, 0, 0, 0.55);
  }
  50% {
    box-shadow:
      0 0 0 7px rgba(201, 169, 232, 0.9),
      0 0 0 9999px rgba(0, 0, 0, 0.55);
  }
}

/* Карточка тура */
.tour-card {
  position: fixed;
  width: 320px;
  background: var(--bg-primary, white);
  border-radius: 20px;
  padding: 24px;
  box-shadow:
    0 24px 60px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(201, 169, 232, 0.3);
  z-index: 10001;
  animation: card-appear 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes card-appear {
  from {
    opacity: 0;
    transform: scale(0.85) translateY(8px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Прогресс-точки */
.tour-progress {
  display: flex;
  gap: 6px;
  margin-bottom: 16px;
  justify-content: center;
}

.tour-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--border-color, #e0e0e0);
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.tour-dot.active {
  background: var(--primary-color, #c9a9e8);
  width: 24px;
  border-radius: 4px;
}

.tour-dot.done {
  background: var(--primary-color, #c9a9e8);
  opacity: 0.5;
}

.tour-dot:hover {
  opacity: 1 !important;
  background: var(--primary-color, #c9a9e8);
}

/* Иконка */
.tour-step-icon {
  font-size: 36px;
  text-align: center;
  margin-bottom: 10px;
  line-height: 1;
}

/* Заголовок */
.tour-title {
  margin: 0 0 8px 0;
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary, #1a1a1a);
  text-align: center;
  line-height: 1.3;
}

/* Описание */
.tour-text {
  margin: 0 0 20px 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-secondary, #666);
  text-align: center;
}

/* Кнопки */
.tour-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.tour-skip {
  background: none;
  border: none;
  font-size: 13px;
  color: var(--text-tertiary, #999);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.2s;
  white-space: nowrap;
}

.tour-skip:hover {
  color: var(--text-secondary, #666);
  background: var(--hover-bg, #f5f5f5);
}

.tour-nav {
  display: flex;
  gap: 8px;
}

.tour-btn {
  padding: 8px 16px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
  white-space: nowrap;
}

.tour-btn-prev {
  background: var(--bg-secondary, #f5f5f5);
  color: var(--text-secondary, #666);
}

.tour-btn-prev:hover {
  background: var(--border-color, #e0e0e0);
}

.tour-btn-next {
  background: var(--primary-color, #c9a9e8);
  color: white;
}

.tour-btn-next:hover {
  background: var(--primary-hover, #b794d4);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(201, 169, 232, 0.4);
}

/* Счётчик */
.tour-counter {
  text-align: center;
  font-size: 11px;
  color: var(--text-tertiary, #bbb);
  margin-top: 12px;
  letter-spacing: 0.5px;
}

/* Мобильная адаптация */
@media (max-width: 480px) {
  .tour-card {
    width: calc(100vw - 32px);
    left: 16px !important;
    right: 16px !important;
    bottom: 16px !important;
    top: auto !important;
    transform: none !important;
  }
}
</style>
