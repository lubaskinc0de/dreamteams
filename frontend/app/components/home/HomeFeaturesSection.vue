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
  <section class="relative py-12 sm:py-16 md:py-20 overflow-hidden">
    <!-- Background with pattern -->
    <div class="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-success-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900"></div>
    <div class="absolute inset-0 opacity-[0.03] dark:opacity-[0.05]" style="background-image: url('data:image/svg+xml,%3Csvg width=&quot;60&quot; height=&quot;60&quot; viewBox=&quot;0 0 60 60&quot; xmlns=&quot;http://www.w3.org/2000/svg&quot;%3E%3Cg fill=&quot;none&quot; fill-rule=&quot;evenodd&quot;%3E%3Cg fill=&quot;%239C92AC&quot; fill-opacity=&quot;1&quot;%3E%3Cpath d=&quot;M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z&quot;/%3E%3C/g%3E%3C/g%3E%3C/svg%3E');"></div>

    <UContainer class="relative z-10">
      <div class="text-center mb-8 sm:mb-12 md:mb-16 fade-in-scroll">
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-extrabold mb-3 sm:mb-4">
          <span class="bg-gradient-to-r from-primary-600 via-primary-500 to-success-600 dark:from-primary-400 dark:via-primary-300 dark:to-success-400 bg-clip-text text-transparent">
            {{ t('home.featuresTitle') }}
          </span>
        </h2>
        <p class="text-base sm:text-lg md:text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
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
