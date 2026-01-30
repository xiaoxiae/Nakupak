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
  <ItemCard
    v-for="entry in items"
    :key="entry.id"
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
</template>
