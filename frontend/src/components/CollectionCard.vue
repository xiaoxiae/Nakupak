<template>
  <div class="bg-surface-secondary border border-border rounded-xl p-4">
    <div class="flex items-center justify-between mb-3">
      <slot name="header" />
      <div class="flex items-center gap-2">
        <slot name="actions" />
      </div>
    </div>
    <div class="flex flex-wrap gap-2">
      <slot />
    </div>
  </div>
</template>
