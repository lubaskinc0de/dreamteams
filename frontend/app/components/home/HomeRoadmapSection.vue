<script setup lang="ts">
interface RoadmapItem {
  icon: string;
  title: string;
  description: string;
  status: string;
}

interface Props {
  items: RoadmapItem[];
}

defineProps<Props>();

const { t } = useI18n();
</script>

<template>
  <section class="py-12 sm:py-16 md:py-20 bg-gray-50 dark:bg-gray-950">
    <UContainer>
      <div class="max-w-3xl mb-8 sm:mb-12 md:mb-16 fade-in-scroll">
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-extrabold mb-4 text-gray-900 dark:text-white">
          {{ t('home.roadmap.title') }}
        </h2>
        <p class="text-base sm:text-lg md:text-xl text-gray-600 dark:text-gray-400">
          {{ t('home.roadmap.description') }}
        </p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 stagger-children">
        <UCard
          v-for="(item, index) in items"
          :key="index"
          variant="outline"
          class="h-full"
        >
          <div class="flex items-center justify-between gap-4 mb-6">
            <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-primary-500/10 text-primary-600 dark:text-primary-400">
              <UIcon :name="item.icon" class="text-2xl" />
            </div>
            <UBadge :label="item.status" color="neutral" variant="subtle" />
          </div>

          <h3 class="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white mb-3">
            {{ item.title }}
          </h3>
          <p class="text-sm sm:text-base text-gray-600 dark:text-gray-400 leading-relaxed">
            {{ item.description }}
          </p>
        </UCard>
      </div>
    </UContainer>
  </section>
</template>
