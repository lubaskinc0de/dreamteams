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
  <section class="py-16 sm:py-20 bg-white dark:bg-gray-900">
    <UContainer>
      <div class="text-center mb-12 sm:mb-16 px-4 fade-in-scroll">
        <h2 class="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
          {{ t('home.whyBest.title') }}
        </h2>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8 max-w-5xl mx-auto px-4 stagger-children">
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
