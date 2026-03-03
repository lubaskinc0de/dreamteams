<script setup lang="ts">
/**
 * Empty state for competitions preview list
 */

const { t } = useI18n();
const emit = defineEmits(["place-competition"]);
</script>

<template>
  <div class="flex flex-col items-center justify-center py-20 px-4 text-center">
    <div class="size-20 rounded-2xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-6">
      <UIcon
        name="i-heroicons-magnifying-glass"
        class="size-10 text-gray-400 dark:text-gray-500"
      />
    </div>
    <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">
      {{ t("competitionsPreview.empty.title") }}
    </h3>
    <p class="text-gray-500 dark:text-gray-400 mb-8 max-w-sm">
      {{ t("competitionsPreview.empty.description") }}
    </p>
    <UButton
      :label="t('competitionsPreview.empty.placeButton')"
      icon="i-heroicons-plus"
      size="lg"
      @click="emit('place-competition')"
    />
  </div>
</template>
