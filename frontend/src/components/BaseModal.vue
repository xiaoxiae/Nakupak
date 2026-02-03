<script setup>
import { X } from 'lucide-vue-next'
import { Motion, AnimatePresence } from 'motion-v'

defineProps({
  show: Boolean,
  title: String
})

const emit = defineEmits(['close'])

function close() {
  emit('close')
}
</script>

<template>
  <Teleport to="body">
  <AnimatePresence>
    <Motion
      v-if="show"
      :initial="{ opacity: 0 }"
      :animate="{ opacity: 1 }"
      :exit="{ opacity: 0 }"
      :transition="{ duration: 0.15 }"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      @click.self="close"
    >
      <Motion
        :initial="{ opacity: 0, scale: 0.95, y: 10 }"
        :animate="{ opacity: 1, scale: 1, y: 0 }"
        :exit="{ opacity: 0, scale: 0.95, y: 10 }"
        :transition="{ duration: 0.15, ease: 'easeOut' }"
        class="bg-surface border border-border rounded-xl w-full max-w-md max-h-[90vh] flex flex-col"
      >
        <div class="flex items-center justify-between p-6 pb-4 border-b border-border shrink-0">
          <h3 class="font-semibold text-text">{{ title }}</h3>
          <button @click="close" class="text-text-muted hover:text-text">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="overflow-y-auto px-6 py-4">
          <slot />
        </div>

        <div class="flex gap-2 justify-end px-6 py-4 border-t border-border shrink-0">
          <slot name="footer" />
        </div>
      </Motion>
    </Motion>
  </AnimatePresence>
  </Teleport>
</template>
