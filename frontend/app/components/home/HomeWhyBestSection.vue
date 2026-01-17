<script setup lang="ts">
/**
 * Why we're the best section
 */

interface WhyBestItem {
  icon: string;
  title: string;
  description: string;
}

interface Props {
  items: WhyBestItem[];
}

const props = defineProps<Props>();
const { t } = useI18n();
</script>

<template>
  <section class="relative py-12 sm:py-16 md:py-20 overflow-hidden bg-gradient-to-b from-white via-gray-50 to-white dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
    <UContainer>
      <div class="text-center mb-8 sm:mb-12 md:mb-16 fade-in-scroll">
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-extrabold mb-4">
          <span class="bg-gradient-to-r from-primary-600 via-success-600 to-primary-500 dark:from-primary-400 dark:via-success-400 dark:to-primary-300 bg-clip-text text-transparent">
            {{ t('home.whyBest.title') }}
          </span>
        </h2>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8 max-w-5xl mx-auto stagger-children">
        <UCard
          v-for="(item, index) in items"
          :key="index"
          variant="soft"
          class="card-hover-smooth"
        >
          <div class="flex items-start gap-3 sm:gap-4">
            <div class="p-2 sm:p-3 rounded-xl bg-gradient-to-br from-primary-500/20 to-success-500/20 flex-shrink-0">
              <UIcon :name="item.icon" class="text-2xl sm:text-3xl text-primary-600 dark:text-primary-400" />
            </div>
            <div>
              <h3 class="text-lg sm:text-xl font-bold text-gray-900 dark:text-white mb-2 break-words">
                {{ item.title }}
              </h3>
              <p class="text-sm sm:text-base text-gray-600 dark:text-gray-400 leading-relaxed break-words">
                {{ item.description }}
              </p>
            </div>
          </div>
        </UCard>
      </div>
    </UContainer>
  </section>
</template>
