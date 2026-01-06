<script setup lang="ts">
/**
 * Final call-to-action section
 */

interface Emits {
  'start': [];
}

const emit = defineEmits(['start']);
const { t } = useI18n();
</script>

<template>
  <section class="py-16 sm:py-20 relative overflow-hidden bg-gradient-to-r from-primary-600/10 via-success-600/10 to-primary-600/10 dark:from-primary-600/20 dark:via-success-600/20 dark:to-primary-600/20">
    <UContainer>
      <div class="text-center max-w-3xl mx-auto px-4 scale-in-scroll">
        <h2 class="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-3 sm:mb-4">
          {{ t('home.cta.title') }}
        </h2>
        <p class="text-base sm:text-lg text-gray-600 dark:text-gray-300 mb-6 sm:mb-8">
          {{ t('home.cta.description') }}
        </p>
        <UButton
          @click="emit('start')"
          color="primary"
          size="xl"
          icon="i-heroicons-rocket-launch"
        >
          {{ t('home.startButton') }}
        </UButton>
      </div>
    </UContainer>
  </section>
</template>
