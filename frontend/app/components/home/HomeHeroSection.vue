<script setup lang="ts">
/**
 * Hero section with brand name and CTA
 */
const { t } = useI18n();
</script>

<template>
  <section class="relative overflow-hidden min-h-[34rem] sm:min-h-[40rem] bg-white dark:bg-gray-950">
    <div class="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-primary-100/40 dark:from-gray-950 dark:via-gray-900 dark:to-primary-950/30" />
    <div class="absolute -top-16 left-[8%] h-40 w-40 rounded-full bg-primary-400/20 blur-3xl animate-pulse" />
    <div class="absolute top-[18%] right-[12%] h-56 w-56 rounded-full bg-primary-300/15 blur-3xl animate-pulse [animation-delay:900ms]" />
    <div class="absolute bottom-[10%] left-[22%] h-48 w-48 rounded-full bg-primary-500/10 blur-3xl animate-pulse [animation-delay:1600ms]" />
    <div class="absolute -bottom-20 right-[18%] h-64 w-64 rounded-full bg-primary-400/12 blur-3xl animate-pulse [animation-delay:500ms]" />

    <UContainer class="relative z-10 flex min-h-[34rem] sm:min-h-[40rem] items-center py-16 sm:py-24">
      <div class="max-w-4xl">
        <p class="mb-4 text-sm font-semibold uppercase tracking-[0.24em] text-primary-600 dark:text-primary-300 fade-in-scroll">
          {{ t('nav.brandSubtitle') }}
        </p>
        <h1 class="text-5xl sm:text-6xl lg:text-7xl font-extrabold mb-6 text-gray-900 dark:text-white scale-in-scroll">
          <span class="whitespace-nowrap">
            {{ t('home.title') }}
          </span>
        </h1>

        <p class="max-w-3xl text-lg sm:text-xl lg:text-2xl font-medium text-gray-900 dark:text-gray-100 mb-4 fade-in-scroll">
          {{ t('home.heroTitle') }}
        </p>
        <p class="max-w-3xl text-base sm:text-lg text-gray-600 dark:text-gray-300 mb-8 fade-in-scroll">
          {{ t('home.heroDescription') }}
        </p>

        <div class="fade-in-scroll flex flex-col sm:flex-row gap-3 justify-start">
          <UButton
            @click="navigateTo('/competitions')"
            size="xl"
            icon="i-heroicons-magnifying-glass"
            color="primary"
            variant="solid"
            class="w-full sm:w-auto sm:min-w-[220px]"
            :ui="{ base: 'justify-center' }"
          >
            {{ t('home.findHackathonButton') }}
          </UButton>
          <UButton
            @click="navigateTo('/onboarding')"
            size="xl"
            icon="i-heroicons-building-office-2"
            color="neutral"
            variant="soft"
            class="w-full sm:w-auto sm:min-w-[220px]"
            :ui="{ base: 'justify-center' }"
          >
            {{ t('home.registerButton') }}
          </UButton>
        </div>
      </div>
    </UContainer>
  </section>
</template>
