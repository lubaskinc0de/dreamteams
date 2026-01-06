<script setup lang="ts">
/**
 * Hero section with brand name, title, CTA, and stats
 */
import type { Stat } from "~/types/ui";

interface Props {
  stats: Stat[];
}

interface Emits {
  'start': [];
}

const props = defineProps<Props>();
const emit = defineEmits(['start']);

const { t } = useI18n();
</script>

<template>
  <section class="relative overflow-hidden py-16 sm:py-24 lg:py-32 bg-gradient-to-br from-primary-500/10 via-success-500/5 to-primary-500/10 dark:from-primary-500/20 dark:via-success-500/10 dark:to-primary-500/20">
    <!-- Background Decoration -->
    <div class="absolute top-0 right-0 w-72 h-72 sm:w-96 sm:h-96 bg-primary-500/20 rounded-full blur-3xl animate-pulse"></div>
    <div class="absolute bottom-0 left-0 w-72 h-72 sm:w-96 sm:h-96 bg-success-500/20 rounded-full blur-3xl animate-pulse [animation-delay:1000ms]"></div>

    <UContainer>
      <div class="text-center max-w-4xl mx-auto">
        <!-- Brand Name -->
        <h1 class="text-6xl sm:text-7xl md:text-8xl lg:text-9xl font-extrabold mb-4 sm:mb-6 scale-in-scroll">
          <span class="bg-gradient-to-r from-primary-600 to-success-600 dark:from-primary-400 dark:to-success-400 bg-clip-text text-transparent">
            {{ t('home.title') }}
          </span>
        </h1>

        <!-- Slogan -->
        <p class="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-bold text-gray-900 dark:text-white mb-6 sm:mb-8 fade-in-scroll">
          {{ t('home.heroTitle') }}
        </p>

        <!-- CTA Text -->
        <p class="text-base sm:text-lg md:text-xl font-semibold text-primary-600 dark:text-primary-400 mb-8 sm:mb-10 max-w-2xl mx-auto px-4 fade-in-scroll">
          {{ t('home.ctaText') }}
        </p>

        <!-- CTA Buttons -->
        <div class="flex flex-col sm:flex-row gap-4 justify-center mb-12 sm:mb-16 fade-in-scroll">
          <UButton
            @click="emit('start')"
            size="xl"
            icon="i-heroicons-rocket-launch"
            color="primary"
            variant="solid"
            class="!px-8 !py-4 !text-lg sm:!text-xl"
          >
            {{ t('home.startButton') }}
          </UButton>
        </div>

        <!-- Stats Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 max-w-4xl mx-auto px-4 stagger-children">
          <UCard
            v-for="(stat, index) in stats"
            :key="index"
            variant="soft"
            class="card-hover-smooth"
          >
            <div class="flex items-center justify-center gap-2 sm:gap-3 mb-2">
              <UIcon :name="stat.icon" :class="['text-2xl sm:text-3xl', stat.color]" />
              <span class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-gray-100">
                {{ stat.value }}
              </span>
            </div>
            <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 text-center">{{ stat.label }}</p>
          </UCard>
        </div>
      </div>
    </UContainer>
  </section>
</template>
