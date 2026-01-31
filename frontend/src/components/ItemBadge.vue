<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Motion } from 'motion-v'
import { formatQuantity } from '../utils/units'

const { t } = useI18n()

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  count: {
    type: Number,
    default: null,
  },
  countStyle: {
    type: String,
    default: 'x',
    validator: (value) => ['parentheses', 'x'].includes(value),
  },
  unit: {
    type: String,
    default: null,
  },
  checked: {
    type: Boolean,
    default: null,
  },
  clickable: {
    type: Boolean,
    default: false,
  },
  selected: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['click'])

const isPressed = ref(false)

function handleClick(e) {
  if (props.clickable) {
    e.stopPropagation()
    isPressed.value = true
    emit('click')
    setTimeout(() => isPressed.value = false, 150)
  }
}
</script>

<template>
  <Motion
    :as="clickable ? 'button' : 'span'"
    class="inline-flex shrink-0 items-center gap-2 px-2 py-1.5 rounded-lg text-sm font-medium"
    :class="{
      'hover:opacity-80 cursor-pointer': clickable,
      'opacity-50': checked === false,
      'bg-primary text-white': selected,
      'bg-surface-tertiary text-text': !selected,
    }"
    :animate="{ scale: isPressed ? 0.9 : 1 }"
    :transition="{ duration: 0.1 }"
    @click="handleClick"
  >
    <slot name="prefix" />
    <span>{{ name }}</span>
    <span v-if="count != null && count > 0" class="text-xs" :class="selected ? 'text-white/70' : 'text-text-muted'">
      {{ countStyle === 'parentheses' ? `(${count})` : (unit ? formatQuantity(count, t('units.' + unit)) : `x${count}`) }}
    </span>
  </Motion>
</template>
