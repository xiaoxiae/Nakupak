<script setup>
import ItemCard from './ItemCard.vue'

defineProps({
  items: {
    type: Array,
    required: true,
  },
})

const emit = defineEmits(['increment', 'decrement', 'update-quantity', 'change-unit', 'remove', 'toggle-check'])
</script>

<template>
  <TransitionGroup name="item-reorder" tag="div">
    <div
      v-for="entry in items"
      :key="entry.id"
      class="transition-opacity duration-200"
      :class="{ 'opacity-40': entry.dimmed }"
    >
      <ItemCard
        :item="entry.item"
        :quantity="entry.quantity"
        :unit="entry.unit"
        :recipe-color="entry.recipeColor"
        :checked="entry.checked"
        @increment="emit('increment', entry)"
        @decrement="emit('decrement', entry)"
        @update-quantity="emit('update-quantity', entry, $event)"
        @change-unit="emit('change-unit', entry, $event)"
        @remove="emit('remove', entry)"
        @toggle-check="emit('toggle-check', entry)"
      />
    </div>
  </TransitionGroup>
</template>

<style scoped>
.item-reorder-move {
  transition: transform 0.3s ease;
}
</style>
