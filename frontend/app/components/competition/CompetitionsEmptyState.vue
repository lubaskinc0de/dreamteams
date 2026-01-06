<script setup lang="ts">
/**
 * Empty state for competitions list
 */

const emit = defineEmits(['create']);
const { t } = useI18n();
</script>

<template>
  <UCard class="flex-1">
    <div class="text-center py-12">
      <UIcon
        name="i-heroicons-trophy"
        class="mx-auto h-12 w-12 text-gray-400 dark:text-gray-600 mb-4"
      />
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
        {{ t('competitions.empty') }}
      </h3>
      <p class="text-gray-600 dark:text-gray-400 mb-6">
        {{ t('competitions.emptyDescription') }}
      </p>
      <UButton
        icon="i-heroicons-plus"
        color="primary"
        :label="t('competitions.createButton')"
        @click="emit('create')"
      />
    </div>
  </UCard>
</template>
