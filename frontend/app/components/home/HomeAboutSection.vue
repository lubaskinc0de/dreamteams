<script setup lang="ts">
/**
 * About section with title and description
 */
const { t } = useI18n();
</script>

<template>
  <section class="relative py-12 sm:py-16 md:py-20 overflow-hidden bg-white dark:bg-gray-900">
    <!-- Decorative elements -->
    <div class="absolute top-0 left-0 w-72 h-72 bg-primary-500/10 rounded-full blur-3xl"></div>
    <div class="absolute bottom-0 right-0 w-96 h-96 bg-success-500/10 rounded-full blur-3xl"></div>

    <UContainer class="relative z-10">
      <div class="max-w-3xl mx-auto text-center fade-in-scroll">
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-extrabold mb-4 sm:mb-6 fade-in-left">
          <span class="bg-gradient-to-r from-success-600 via-primary-600 to-primary-500 dark:from-success-400 dark:via-primary-400 dark:to-primary-300 bg-clip-text text-transparent">
            {{ t('home.about.title') }}
          </span>
        </h2>
        <p class="text-lg sm:text-xl md:text-2xl text-gray-600 dark:text-gray-400 leading-relaxed fade-in-right">
          {{ t('home.about.description') }}
        </p>
      </div>
    </UContainer>
  </section>
</template>
