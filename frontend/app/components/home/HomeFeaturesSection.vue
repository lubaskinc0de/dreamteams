<script setup lang="ts">
/**
 * Features section with feature cards grid
 */
import type { Feature } from "~/types/ui";

interface Props {
  features: Feature[];
}

const props = defineProps<Props>();
const { t } = useI18n();
</script>

<template>
  <section class="py-16 sm:py-20 bg-gray-50 dark:bg-gray-800/50">
    <UContainer>
      <div class="text-center mb-12 sm:mb-16 px-4 fade-in-scroll">
        <h2 class="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-3 sm:mb-4">
          {{ t('home.featuresTitle') }}
        </h2>
        <p class="text-base sm:text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          {{ t('home.featuresDescription') }}
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 px-4 stagger-children">
        <UCard
          v-for="(feature, index) in features"
          :key="index"
          variant="outline"
          class="flex flex-col card-hover-smooth"
        >
          <template #header>
            <div class="flex items-center gap-3 sm:gap-4">
              <div class="p-2 sm:p-3 rounded-xl bg-gradient-to-br from-primary-500/10 to-success-500/10">
                <UIcon :name="feature.icon" class="text-2xl sm:text-3xl text-primary-600 dark:text-primary-400" />
              </div>
              <h3 class="text-base sm:text-lg md:text-xl font-semibold text-gray-900 dark:text-white">
                {{ feature.title }}
              </h3>
            </div>
          </template>

          <p class="text-sm sm:text-base text-gray-600 dark:text-gray-400 leading-relaxed flex-grow break-words">
            {{ feature.description }}
          </p>

          <template #footer>
            <UBadge
              :label="feature.badge.label"
              :color="feature.badge.color"
              variant="subtle"
              size="sm"
            />
          </template>
        </UCard>
      </div>
    </UContainer>
  </section>
</template>
