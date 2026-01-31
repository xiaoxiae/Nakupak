<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: v => ['primary', 'secondary', 'danger', 'success', 'outline'].includes(v),
  },
  size: {
    type: String,
    default: 'md',
    validator: v => ['sm', 'md'].includes(v),
  },
  disabled: Boolean,
  block: Boolean,
  fab: Boolean,
})

const variantClasses = {
  primary: 'bg-primary text-white hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed',
  secondary: 'bg-surface-secondary text-text-secondary hover:opacity-80',
  danger: 'bg-danger text-white hover:opacity-90',
  success: 'bg-success text-white hover:opacity-90',
  outline: 'bg-surface text-text border border-border hover:opacity-80',
}

const sizeClasses = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-6 py-3',
}

const classes = computed(() => [
  'flex items-center justify-center gap-2 rounded-lg font-medium',
  variantClasses[props.variant],
  sizeClasses[props.size],
  props.block && 'w-full',
  props.fab && 'rounded-xl shadow-lg',
])
</script>

<template>
  <button :class="classes" :disabled="disabled">
    <slot />
  </button>
</template>
