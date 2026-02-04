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
    class="flex items-center bg-surface-secondary border border-border rounded-lg mb-2 border-l-4"
    :style="{ borderLeftColor: accentColor || 'var(--border)' }"
  >
    <div
      class="flex items-center flex-1 min-w-0 px-4 py-3"
      :class="{ 'cursor-pointer': clickable }"
      @click="clickable && emit('click')"
    >
      <slot name="prefix"></slot>
      <CheckBox v-if="checked !== null" class="mr-2" :checked="checked" @toggle="emit('toggleCheck')" />
      <div class="flex-1 min-w-0 flex items-start gap-2" :class="{ 'opacity-40': checked === true }">
        <span class="font-medium min-w-0 break-words text-text">{{ name }}</span>
        <span
          v-if="category"
          class="shrink-0 px-1.5 py-0.5 rounded text-[10px] tracking-wide uppercase"
          :style="{ backgroundColor: category.color + '20', color: category.color }"
        >
          {{ category.name }}
        </span>
      </div>
    </div>
    <div class="pr-4">
      <slot name="actions"></slot>
    </div>
  </div>
</template>
