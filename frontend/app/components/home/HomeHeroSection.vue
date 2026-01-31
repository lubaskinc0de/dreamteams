<script setup lang="ts">
/**
 * Hero section with brand name and CTA
 */
const emit = defineEmits(['start']);
const { t } = useI18n();
</script>

<template>
  <section class="relative overflow-hidden py-16 sm:py-24 lg:py-32 bg-gradient-to-br from-primary-500/10 via-success-500/5 to-primary-500/10 dark:from-primary-500/20 dark:via-success-500/10 dark:to-primary-500/20">
    <!-- Background Decoration -->
    <div class="absolute top-0 right-0 w-72 h-72 sm:w-96 sm:h-96 bg-primary-500/20 rounded-full blur-3xl animate-pulse"></div>
    <div class="absolute bottom-0 left-0 w-72 h-72 sm:w-96 sm:h-96 bg-success-500/20 rounded-full blur-3xl animate-pulse [animation-delay:1000ms]"></div>

    <UContainer>
      <div class="text-left sm:text-center max-w-4xl mx-auto">
        <!-- Brand Name -->
        <h1 class="text-[clamp(2.5rem,12vw,6rem)] sm:text-7xl md:text-8xl lg:text-9xl font-extrabold mb-6 sm:mb-8 scale-in-scroll">
          <span class="bg-gradient-to-r from-primary-600 to-success-600 dark:from-primary-400 dark:to-success-400 bg-clip-text text-transparent whitespace-nowrap">
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
            @click="emit('start')"
            size="xl"
            icon="i-heroicons-rocket-launch"
            color="primary"
            variant="solid"
            class="min-w-[200px]"
            :ui="{ base: 'justify-center' }"
          >
            {{ t('home.startButton') }}
          </UButton>
        </div>
      </div>
    </UContainer>
  </section>
</template>
