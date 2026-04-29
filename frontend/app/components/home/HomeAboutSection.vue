<script setup lang="ts">
/**
 * About section with photos background
 */
const { t } = useI18n();

// Split photos into 3 columns
const column1 = [1, 2, 3, 4, 5, 6, 7, 8];
const column2 = [9, 10, 11, 12, 13, 14, 15, 16];
const column3 = [17, 18, 19, 20, 21, 22, 23, 24];
</script>

<template>
  <section class="relative w-full py-32 md:py-40 overflow-hidden bg-gray-100 dark:bg-gray-900">
    <!-- Photos Background with Marquee -->
    <!-- First column - reverse (visible only from xl - left position) -->
    <UMarquee
      reverse
      orientation="vertical"
      :overlay="false"
      :repeat="2"
      :ui="{
        root: 'hidden xl:flex [--duration:40s] absolute w-[360px] left-[3%] -top-[300px] h-[940px] transform-3d rotate-x-55 rotate-y-0 rotate-z-30'
      }"
    >
      <img
        v-for="i in column1"
        :key="`col1-${i}`"
        :src="`/photos/photo${i}.webp`"
        width="360"
        height="240"
        :alt="`DreamTeams Photo ${i}`"
        class="aspect-video border-2 border-primary-200 dark:border-primary-800 rounded-lg bg-white shadow-lg will-change-transform"
        loading="lazy"
      />
    </UMarquee>

    <!-- Second column - normal (centered on mobile, left on tablet, center on xl+) -->
    <UMarquee
      orientation="vertical"
      :overlay="false"
      :repeat="2"
      :ui="{
        root: '[--duration:40s] absolute w-[min(280px,calc(100vw-2rem))] md:w-[360px] -top-[400px] left-1/2 -translate-x-1/2 md:translate-x-0 md:left-[8%] xl:left-[38%] h-[1160px] transform-3d rotate-x-55 rotate-y-0 rotate-z-30'
      }"
    >
      <img
        v-for="i in column2"
        :key="`col2-${i}`"
        :src="`/photos/photo${i}.webp`"
        width="360"
        height="240"
        :alt="`DreamTeams Photo ${i}`"
        class="aspect-video border-2 border-primary-200 dark:border-primary-800 rounded-lg bg-white shadow-lg will-change-transform"
        loading="lazy"
      />
    </UMarquee>

    <!-- Third column - reverse (visible from md - right position) -->
    <UMarquee
      reverse
      orientation="vertical"
      :overlay="false"
      :repeat="2"
      :ui="{
        root: 'hidden md:flex [--duration:40s] absolute w-[360px] -top-[300px] right-[8%] xl:right-[3%] h-[1060px] transform-3d rotate-x-55 rotate-y-0 rotate-z-30'
      }"
    >
      <img
        v-for="i in column3"
        :key="`col3-${i}`"
        :src="`/photos/photo${i}.webp`"
        width="360"
        height="240"
        :alt="`DreamTeams Photo ${i}`"
        class="aspect-video border-2 border-primary-200 dark:border-primary-800 rounded-lg bg-white shadow-lg will-change-transform"
        loading="lazy"
      />
    </UMarquee>

    <!-- Content overlay -->
    <div class="absolute inset-0 bg-gradient-to-b from-white/80 via-white/60 to-white/80 dark:from-gray-900/80 dark:via-gray-900/60 dark:to-gray-900/80 flex items-center justify-center z-10">
      <UContainer>
        <div class="max-w-3xl mx-auto text-center fade-in-scroll">
          <h2 class="text-3xl sm:text-4xl md:text-5xl font-extrabold mb-4 sm:mb-6">
            <span class="text-primary-600 dark:text-primary-400">
              {{ t('home.about.title') }}
            </span>
          </h2>
          <p class="text-lg sm:text-xl md:text-2xl text-gray-700 dark:text-gray-300 leading-relaxed font-medium">
            {{ t('home.about.description') }}
          </p>
        </div>
      </UContainer>
    </div>
  </section>
</template>
