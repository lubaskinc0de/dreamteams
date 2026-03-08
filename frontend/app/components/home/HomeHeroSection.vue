<script setup lang="ts">
/**
 * Hero section with brand name and CTA
 */
const { t } = useI18n();
</script>

<template>
  <section class="relative overflow-hidden py-16 sm:py-24 lg:py-32 bg-gradient-to-br from-primary-50 to-primary-100/50 dark:from-primary-950/30 dark:to-primary-900/20">
    <!-- Background Decoration -->
    <div class="absolute top-0 right-0 w-72 h-72 sm:w-96 sm:h-96 bg-primary-500/20 rounded-full blur-3xl animate-pulse"></div>
    <div class="absolute bottom-0 left-0 w-72 h-72 sm:w-96 sm:h-96 bg-primary-500/20 rounded-full blur-3xl animate-pulse [animation-delay:1000ms]"></div>

    <UContainer>
      <div class="text-left sm:text-center max-w-4xl mx-auto">
        <!-- Brand Name -->
        <h1 class="text-[clamp(2.5rem,12vw,6rem)] sm:text-7xl md:text-8xl lg:text-9xl font-extrabold mb-6 sm:mb-8 scale-in-scroll">
          <span class="text-primary-600 dark:text-primary-400 whitespace-nowrap">
            {{ t('home.title') }}
          </span>
        </h1>

        <!-- CTA Text -->
        <p class="text-lg sm:text-xl md:text-2xl lg:text-3xl font-semibold text-gray-700 dark:text-gray-300 mb-8 sm:mb-10 max-w-3xl sm:mx-auto fade-in-scroll">
          {{ t('home.ctaText') }}
        </p>

        <!-- CTA Button -->
        <div class="fade-in-scroll flex justify-start sm:justify-center">
          <UButton
            @click="navigateTo('/competitions')"
            size="xl"
            icon="i-heroicons-magnifying-glass"
            color="primary"
            variant="solid"
            class="min-w-[200px]"
            :ui="{ base: 'justify-center' }"
          >
            {{ t('home.findHackathonButton') }}
          </UButton>
        </div>
      </div>
    </UContainer>
  </section>
</template>
