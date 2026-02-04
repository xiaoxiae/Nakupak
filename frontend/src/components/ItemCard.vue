<script setup>
import { ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { ChevronUp, ChevronDown, X } from 'lucide-vue-next'
import { Motion } from 'motion-v'
import ItemRow from './ItemRow.vue'
import IconButton from './IconButton.vue'
import { UNITS, getUnit, formatQuantity } from '../utils/units'

const { t } = useI18n()

const props = defineProps({
  item: Object,
  quantity: Number,
  unit: {
    type: String,
    default: 'x',
  },
  recipeColor: String,
  checked: {
    type: Boolean,
    default: null,
  },
})

const emit = defineEmits(['increment', 'decrement', 'remove', 'changeUnit', 'updateQuantity', 'toggleCheck'])

const quantityScale = ref(1)
const editing = ref(false)
const editValue = ref('')
const editUnit = ref(props.unit)
const selectorRef = ref(null)
const quantityInputRef = ref(null)

watch(() => props.quantity, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    quantityScale.value = 0.97
    setTimeout(() => quantityScale.value = 1, 60)
  }
})

function startEditing() {
  editValue.value = String(parseFloat(props.quantity.toFixed(2)))
  editUnit.value = props.unit
  editing.value = true
  nextTick(() => {
    quantityInputRef.value?.focus()
    quantityInputRef.value?.select()
  })
}

function stopEditing(save) {
  if (!editing.value) return
  editing.value = false
  if (save) {
    const parsed = parseFloat(editValue.value.replace(/[^\d.]/g, ''))
    const unitChanged = editUnit.value !== props.unit
    const qtyChanged = !isNaN(parsed) && parsed !== props.quantity
    if (unitChanged) {
      emit('changeUnit', editUnit.value)
      // Also emit the quantity shown in the editor (which was updated to the
      // new unit's default in selectUnit) so the caller doesn't have to guess.
      if (!isNaN(parsed)) {
        emit('updateQuantity', parsed)
      }
    } else if (qtyChanged) {
      emit('updateQuantity', parsed)
    }
  }
}

function selectUnit(unitValue) {
  editUnit.value = unitValue
  editValue.value = String(getUnit(unitValue).defaultQty)
}

function handleInput() {
  const unitNames = new Map()
  for (const u of UNITS) {
    unitNames.set(u.value.toLowerCase(), u.value)
    const localized = t('units.' + u.value).toLowerCase()
    if (localized !== u.value.toLowerCase()) {
      unitNames.set(localized, u.value)
    }
  }
  const suffixes = [...unitNames.keys()].sort((a, b) => b.length - a.length).map(s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
  const re = new RegExp(`^(\\d+\\.?\\d*)\\s*(${suffixes.join('|')})$`, 'i')
  const m = editValue.value.match(re)
  if (m) {
    editValue.value = m[1]
    editUnit.value = unitNames.get(m[2].toLowerCase())
  }
}

function handleClickOutside(e) {
  if (!editing.value) return
  if (selectorRef.value && !selectorRef.value.contains(e.target)) {
    stopEditing(true)
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside, true)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside, true)
})
</script>

<template>
  <Motion
    :animate="{ scale: quantityScale }"
    :transition="{ duration: 0.06, ease: 'easeOut' }"
    :style="{ transformOrigin: 'center', position: 'relative', zIndex: editing ? 50 : 'auto' }"
  >
    <div class="flex items-center gap-2">
      <ItemRow
        :name="item.name"
        :accent-color="item.category?.color"
        :checked="checked"
        :clickable="checked !== null"
        class="flex-1 min-w-0"
        @click="emit('toggleCheck')"
        @toggle-check="emit('toggleCheck')"
      >
        <template #actions>
          <div class="flex items-center gap-1" @click.stop>
            <div class="relative" ref="selectorRef">
              <div class="flex items-center" v-if="editing">
                <input
                  ref="quantityInputRef"
                  v-model="editValue"
                  type="text"
                  inputmode="decimal"
                  class="w-16 text-center font-semibold text-lg text-text bg-transparent border-b border-primary outline-none px-1 py-0"
                  @input="handleInput"
                  @keydown.enter="stopEditing(true)"
                  @keydown.escape="stopEditing(false)"
                />
                <span class="font-semibold text-lg text-text pl-1">
                  {{ t('units.' + editUnit) }}
                </span>
              </div>
              <button
                v-else
                class="text-center font-semibold text-lg text-text px-1 rounded hover:bg-surface-secondary transition-colors"
                @click="startEditing"
              >
                {{ formatQuantity(quantity, t('units.' + unit)) }}
              </button>
              <div
                v-if="editing"
                class="absolute top-full left-1/2 -translate-x-1/2 mt-1 flex gap-1 bg-surface border border-border rounded-full px-1 py-1 shadow-lg z-50"
              >
                <button
                  v-for="u in UNITS"
                  :key="u.value"
                  class="px-2.5 py-1 rounded-full text-xs font-medium transition-colors whitespace-nowrap"
                  :class="u.value === editUnit
                    ? 'bg-primary text-white'
                    : 'text-text-secondary hover:bg-surface-secondary'"
                  @click="selectUnit(u.value)"
                >
                  {{ t('units.' + u.value) }}
                </button>
              </div>
            </div>
            <div class="flex flex-col">
              <IconButton tiny @click="emit('increment')">
                <ChevronUp class="w-4 h-4" />
              </IconButton>
              <IconButton tiny @click="emit('decrement')">
                <ChevronDown class="w-4 h-4" />
              </IconButton>
            </div>
          </div>
        </template>
      </ItemRow>
      <IconButton small class="mb-2" @click="emit('remove')">
        <X class="w-5 h-5" />
      </IconButton>
    </div>
  </Motion>
</template>
