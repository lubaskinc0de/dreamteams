<script setup lang="ts">
/**
 * Testimonials section with marquee
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
    <div class="absolute inset-0 bg-gradient-to-br from-primary-50/30 via-white to-white dark:from-gray-900 dark:via-gray-800 dark:to-gray-900"></div>
    <div class="absolute top-0 right-0 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl"></div>
    <div class="absolute bottom-0 left-0 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl"></div>

    <!-- Title in container -->
    <UContainer class="relative z-10 mb-8 sm:mb-12 md:mb-16">
      <div class="text-center fade-in-scroll">
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-extrabold mb-4">
          <span class="text-primary-600 dark:text-primary-400">
            {{ t('home.testimonials.title') }}
          </span>
        </h2>
        <p class="text-base sm:text-lg md:text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          {{ t('home.testimonials.description') }}
        </p>
      </div>
    </UContainer>

    <!-- Testimonials Marquee - Full Width -->
    <div class="relative z-10">
      <div class="flex flex-col gap-4 w-full">
        <UMarquee
          :overlay="false"
          :repeat="3"
          :ui="{ root: '[--gap:--spacing(4)]', content: 'w-auto py-1 will-change-transform' }"
        >
          <UCard
            v-for="(testimonial, index) in testimonials"
            :key="`testimonial-row1-${testimonial.name}-${index}`"
            variant="soft"
            class="w-72 sm:w-80 shrink-0"
          >
            <div class="flex items-start gap-4 mb-4">
              <UAvatar
                :src="testimonial.avatar"
                :alt="testimonial.name"
                size="lg"
                class="ring-2 ring-primary-500/20"
              />
              <div class="flex-1 min-w-0">
                <h3 class="font-semibold text-gray-900 dark:text-white truncate">
                  {{ testimonial.name }}
                </h3>
                <p class="text-sm text-primary-600 dark:text-primary-400 truncate">
                  {{ testimonial.role }}
                </p>
              </div>
            </div>

            <p class="text-gray-600 dark:text-gray-400 leading-relaxed italic line-clamp-3 before:content-[open-quote] after:content-[close-quote]">
              {{ testimonial.text }}
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
        </UMarquee>

        <UMarquee
          reverse
          :overlay="false"
          :repeat="3"
          :ui="{ root: '[--gap:--spacing(4)]', content: 'w-auto py-1 will-change-transform' }"
        >
          <UCard
            v-for="(testimonial, index) in testimonials"
            :key="`testimonial-row2-${testimonial.name}-${index}`"
            variant="soft"
            class="w-72 sm:w-80 shrink-0"
          >
            <div class="flex items-start gap-4 mb-4">
              <UAvatar
                :src="testimonial.avatar"
                :alt="testimonial.name"
                size="lg"
                class="ring-2 ring-primary-500/20"
              />
              <div class="flex-1 min-w-0">
                <h3 class="font-semibold text-gray-900 dark:text-white truncate">
                  {{ testimonial.name }}
                </h3>
                <p class="text-sm text-primary-600 dark:text-primary-400 truncate">
                  {{ testimonial.role }}
                </p>
              </div>
            </div>

            <p class="text-gray-600 dark:text-gray-400 leading-relaxed italic line-clamp-3 before:content-[open-quote] after:content-[close-quote]">
              {{ testimonial.text }}
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
        </UMarquee>
      </div>
    </div>
  </section>
</template>
