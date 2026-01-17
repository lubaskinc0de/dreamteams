<script setup lang="ts">
/**
 * Header component for competitions list page
 */
const { t } = useI18n();
</script>

<template>
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
      {{ t('competitions.title') }}
    </h1>
    <p class="text-gray-600 dark:text-gray-400">
      {{ t('competitions.description') }}
    </p>
  </div>
</template>
