<script setup>
import { ref, watch } from 'vue'
import { Minus, Plus } from 'lucide-vue-next'
import { Motion } from 'motion-v'
import ItemRow from './ItemRow.vue'
import IconButton from './IconButton.vue'

const props = defineProps({
  item: Object,
  quantity: Number,
  recipeColor: String,
})

const emit = defineEmits(['increment', 'decrement', 'remove'])

const quantityScale = ref(1)
const lastQuantity = ref(props.quantity)

watch(() => props.quantity, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    quantityScale.value = 0.97
    setTimeout(() => quantityScale.value = 1, 60)
  }
})
</script>

<template>
  <Motion
    :animate="{ scale: quantityScale }"
    :transition="{ duration: 0.06, ease: 'easeOut' }"
    style="transform-origin: center"
  >
    <ItemRow
      :name="item.name"
      :category="item.category"
      :accent-color="recipeColor"
    >
      <template #actions>
        <div class="flex items-center gap-2">
          <IconButton @click="emit('decrement')">
            <Minus class="w-5 h-5" />
          </IconButton>
          <span class="min-w-8 text-center font-semibold text-lg text-text">{{ quantity }}</span>
          <IconButton @click="emit('increment')">
            <Plus class="w-5 h-5" />
          </IconButton>
        </div>
      </template>
    </ItemRow>
  </Motion>
</template>
