<script setup lang="ts">
/**
 * Testimonials section with carousel
 */
import type { Testimonial } from "~/types/ui";

interface Props {
  testimonials: Testimonial[];
}

const props = defineProps<Props>();
const { t } = useI18n();
</script>

<template>
  <section class="relative py-12 sm:py-16 md:py-20 overflow-hidden bg-white dark:bg-gray-900">
    <!-- Decorative background -->
    <div class="absolute inset-0 bg-gradient-to-br from-success-50 via-white to-primary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900"></div>
    <div class="absolute top-0 right-0 w-96 h-96 bg-success-500/10 rounded-full blur-3xl"></div>
    <div class="absolute bottom-0 left-0 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl"></div>

    <UContainer class="relative z-10">
      <div class="text-center mb-8 sm:mb-12 md:mb-16 fade-in-scroll">
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-extrabold mb-4">
          <span class="bg-gradient-to-r from-success-600 via-primary-600 to-primary-500 dark:from-success-400 dark:via-primary-400 dark:to-primary-300 bg-clip-text text-transparent">
            {{ t('home.testimonials.title') }}
          </span>
        </h2>
        <p class="text-base sm:text-lg md:text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          {{ t('home.testimonials.description') }}
        </p>
      </div>

      <!-- Testimonials Carousel -->
      <div class="max-w-5xl mx-auto">
        <UCarousel
          :items="testimonials"
          :ui="{
            container: 'gap-6',
            item: 'basis-full md:basis-1/2 lg:basis-1/3',
            prev: 'hidden md:flex',
            next: 'hidden md:flex'
          }"
          :prev="{ icon: 'i-heroicons-chevron-left', color: 'primary', variant: 'soft', size: 'lg', square: true }"
          :next="{ icon: 'i-heroicons-chevron-right', color: 'primary', variant: 'soft', size: 'lg', square: true }"
          arrows
          class="overflow-hidden"
        >
          <template #default="{ item }">
            <UCard variant="soft" class="h-full flex flex-col">
              <div class="flex items-start gap-4 mb-4">
                <UAvatar
                  :src="item.avatar"
                  :alt="item.name"
                  size="lg"
                  class="ring-2 ring-primary-500/20"
                />
                <div class="flex-1 min-w-0">
                  <h3 class="font-semibold text-gray-900 dark:text-white truncate">
                    {{ item.name }}
                  </h3>
                  <p class="text-sm text-primary-600 dark:text-primary-400 truncate">
                    {{ item.role }}
                  </p>
                </div>
              </div>

              <p class="text-gray-600 dark:text-gray-400 leading-relaxed italic flex-grow">
                "{{ item.text }}"
              </p>

              <div class="mt-4 flex gap-1">
                <UIcon
                  v-for="i in 5"
                  :key="i"
                  name="i-heroicons-star-solid"
                  class="text-yellow-400 text-lg"
                />
              </div>
            </UCard>
          </template>
        </UCarousel>
      </div>
    </UContainer>
  </section>
</template>
