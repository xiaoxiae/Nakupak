<script setup>
import CheckBox from './CheckBox.vue'

defineProps({
  name: {
    type: String,
    required: true,
  },
  category: {
    type: Object,
    default: null,
  },
  accentColor: {
    type: String,
    default: null,
  },
  clickable: {
    type: Boolean,
    default: false,
  },
  checked: {
    type: Boolean,
    default: null,
  },
})

const emit = defineEmits(['click', 'toggleCheck'])
</script>

<template>
  <div
    class="flex items-center px-4 h-12 bg-surface-secondary border border-border rounded-lg mb-2 border-l-4"
    :class="{ 'cursor-pointer': clickable }"
    :style="{ borderLeftColor: accentColor || 'var(--border)' }"
    @click="clickable && emit('click')"
  >
    <slot name="prefix"></slot>
    <CheckBox v-if="checked !== null" class="mr-2" :checked="checked" @toggle="emit('toggleCheck')" />
    <div class="flex-1 min-w-0 flex items-center gap-2" :class="{ 'opacity-40': checked === true }">
      <span class="font-medium truncate text-text">{{ name }}</span>
      <span
        v-if="category"
        class="shrink-0 px-1.5 py-0.5 rounded text-[10px] tracking-wide uppercase"
        :style="{ backgroundColor: category.color + '20', color: category.color }"
      >
        {{ category.name }}
      </span>
    </div>
    <slot name="actions"></slot>
  </div>
</template>
