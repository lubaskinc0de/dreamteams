<script setup lang="ts">
/**
 * About section with title and description
 */
const { t } = useI18n();
</script>

<template>
  <section class="py-16 sm:py-20 bg-white dark:bg-gray-900">
    <UContainer>
      <div class="max-w-3xl mx-auto text-center px-4 fade-in-scroll">
        <h2 class="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4 sm:mb-6 fade-in-left">
          {{ t('home.about.title') }}
        </h2>
        <p class="text-base sm:text-lg text-gray-600 dark:text-gray-400 leading-relaxed fade-in-right">
          {{ t('home.about.description') }}
        </p>
      </div>
    </UContainer>
  </section>
</template>
