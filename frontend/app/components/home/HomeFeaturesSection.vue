<script setup lang="ts">
/**
 * Features section split by audience
 */
import type { Feature } from "~/types/ui";

interface Props {
  organizerFeatures: Feature[];
  participantFeatures: Feature[];
}

defineProps<Props>();
const { t } = useI18n();
</script>

<template>
  <div>
    <section class="relative overflow-hidden bg-gray-950 py-14 text-white sm:py-20 md:py-24">
      <div class="absolute inset-0 bg-gradient-to-br from-gray-950 via-gray-900 to-primary-950/70" />
      <div class="absolute inset-0 opacity-[0.08] [background-image:linear-gradient(rgba(191,219,254,0.22)_1px,transparent_1px),linear-gradient(90deg,rgba(191,219,254,0.22)_1px,transparent_1px)] [background-size:34px_34px]" />

      <UContainer class="relative z-10">
        <div class="text-center mb-10 sm:mb-12 fade-in-scroll">
          <h2 class="text-3xl sm:text-4xl md:text-5xl font-extrabold mb-3 sm:mb-4">
            {{ t('home.featuresTitle') }}
          </h2>
          <p class="text-base sm:text-lg md:text-xl text-slate-300 max-w-2xl mx-auto">
            {{ t('home.featuresDescription') }}
          </p>
        </div>

        <div class="grid gap-8 lg:grid-cols-[0.85fr_1.35fr] lg:items-center">
          <div class="max-w-xl fade-in-left">
            <p class="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-primary-200">
              {{ t('home.featuresSections.organizers.eyebrow') }}
            </p>
            <h3 class="mb-4 text-3xl font-bold sm:text-4xl lg:text-5xl">
              {{ t('home.featuresSections.organizers.title') }}
            </h3>
            <p class="text-base leading-relaxed text-slate-300 sm:text-lg">
              {{ t('home.featuresSections.organizers.description') }}
            </p>
          </div>

          <div class="grid gap-4 sm:grid-cols-6 lg:auto-rows-[minmax(11rem,auto)]">
            <article
              v-for="(feature, index) in organizerFeatures"
              :key="`organizer-${index}`"
              class="rounded-lg border border-white/12 bg-white/[0.07] p-5 shadow-2xl shadow-black/10 backdrop-blur-sm"
              :class="[
                index === 0 ? 'sm:col-span-6 lg:col-span-4' : '',
                index === 1 ? 'sm:col-span-3 lg:col-span-2 lg:row-span-2' : '',
                index === 2 ? 'sm:col-span-3 lg:col-span-4' : '',
              ]"
            >
              <div class="mb-5 flex items-center justify-between gap-4">
                <div class="flex h-11 w-11 items-center justify-center rounded-lg bg-primary-400/15 text-primary-200">
                  <UIcon :name="feature.icon" class="text-2xl" />
                </div>
                <span class="text-xs font-semibold tabular-nums text-primary-200/80">
                  0{{ index + 1 }}
                </span>
              </div>
              <h4 class="mb-2 text-lg font-semibold sm:text-xl">
                {{ feature.title }}
              </h4>
              <p class="text-sm leading-relaxed text-slate-300 sm:text-base">
                {{ feature.description }}
              </p>
            </article>
          </div>
        </div>
      </UContainer>
    </section>

    <section class="relative overflow-hidden bg-white py-14 sm:py-20 md:py-24 dark:bg-gray-950">
      <div class="absolute inset-0 bg-gradient-to-br from-white via-primary-50/35 to-white dark:from-gray-950 dark:via-gray-900 dark:to-gray-950" />

      <UContainer class="relative z-10">
        <div class="grid gap-8 lg:grid-cols-[1fr_1fr] lg:items-start">
          <div class="max-w-xl fade-in-left">
            <p class="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-primary-600 dark:text-primary-300">
              {{ t('home.featuresSections.participants.eyebrow') }}
            </p>
            <h3 class="mb-4 text-3xl font-bold text-gray-900 sm:text-4xl lg:text-5xl dark:text-white">
              {{ t('home.featuresSections.participants.title') }}
            </h3>
            <p class="text-base leading-relaxed text-gray-600 sm:text-lg dark:text-gray-400">
              {{ t('home.featuresSections.participants.description') }}
            </p>
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <article
              v-for="(feature, index) in participantFeatures"
              :key="`participant-${index}`"
              class="rounded-lg border border-primary-100 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900"
              :class="index === 0 ? 'sm:col-span-2' : ''"
            >
              <div class="mb-4 flex items-center gap-3">
                <div class="flex h-11 w-11 items-center justify-center rounded-lg bg-primary-500/12 text-primary-600 dark:text-primary-300">
                  <UIcon :name="feature.icon" class="text-2xl" />
                </div>
                <span class="text-xs font-semibold uppercase tracking-[0.16em] text-primary-600/70 dark:text-primary-300/70">
                  {{ t('home.featuresSections.participants.step') }} {{ index + 1 }}
                </span>
              </div>
              <h4 class="mb-2 text-lg font-semibold text-gray-900 sm:text-xl dark:text-white">
                {{ feature.title }}
              </h4>
              <p class="text-sm leading-relaxed text-gray-600 sm:text-base dark:text-gray-400">
                {{ feature.description }}
              </p>
            </article>
          </div>
        </div>
      </UContainer>
    </section>
  </div>
</template>
