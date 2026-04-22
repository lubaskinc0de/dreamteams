<script setup lang="ts">
interface Props {
  text: string;
  ariaLabel?: string;
}

defineProps<Props>();
</script>

<template>
  <UTooltip
    :text="text"
    :content="{ side: 'top', sideOffset: 6, align: 'center' }"
    :ui="{
      content: '!h-auto !items-start max-w-xs py-1.5 leading-snug',
      text: 'whitespace-normal break-words text-left',
    }"
  >
    <button
      type="button"
      tabindex="0"
      class="inline-flex items-center justify-center align-middle p-0.5 rounded-full text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
      :aria-label="ariaLabel ?? text"
    >
      <UIcon name="i-heroicons-question-mark-circle" class="w-3.5 h-3.5" />
    </button>
  </UTooltip>
</template>
