<script setup lang="ts">
/**
 * Final call-to-action section
 */

interface Emits {
  'start': [];
}

const emit = defineEmits(['start']);
const { t } = useI18n();
</script>

<template>
  <section class="relative py-16 sm:py-20 md:py-24 overflow-hidden">
    <!-- Modern Gradient Background -->
    <div class="absolute inset-0 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 dark:from-blue-700 dark:via-indigo-700 dark:to-purple-700"></div>

    <!-- Animated Floating Orbs -->
    <div class="absolute -top-24 -left-24 w-96 h-96 bg-cyan-400/40 rounded-full blur-3xl animate-pulse"></div>
    <div class="absolute -bottom-24 -right-24 w-96 h-96 bg-purple-400/30 rounded-full blur-3xl animate-pulse [animation-delay:1500ms]"></div>
    <div class="absolute top-1/3 right-1/4 w-64 h-64 bg-pink-400/20 rounded-full blur-3xl animate-pulse [animation-delay:3000ms]"></div>
    <div class="absolute bottom-1/3 left-1/4 w-48 h-48 bg-blue-300/25 rounded-full blur-2xl animate-pulse [animation-delay:2000ms]"></div>

    <!-- Geometric Pattern Overlay -->
    <div class="absolute inset-0 opacity-10">
      <div class="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width=&quot;80&quot; height=&quot;80&quot; xmlns=&quot;http://www.w3.org/2000/svg&quot;%3E%3Cdefs%3E%3Cpattern id=&quot;hexagons&quot; width=&quot;80&quot; height=&quot;80&quot; patternUnits=&quot;userSpaceOnUse&quot;%3E%3Cpath d=&quot;M40,0 L70,20 L70,60 L40,80 L10,60 L10,20 Z&quot; fill=&quot;none&quot; stroke=&quot;white&quot; stroke-width=&quot;1&quot;/%3E%3C/pattern%3E%3C/defs%3E%3Crect width=&quot;100%&quot; height=&quot;100%&quot; fill=&quot;url(%23hexagons)&quot; /%3E%3C/svg%3E')]"></div>
    </div>

    <!-- Sparkles Effect -->
    <div class="absolute inset-0">
      <div class="absolute top-1/4 left-1/3 w-2 h-2 bg-white rounded-full animate-pulse"></div>
      <div class="absolute top-2/3 right-1/4 w-1 h-1 bg-white rounded-full animate-pulse [animation-delay:1000ms]"></div>
      <div class="absolute bottom-1/4 left-1/2 w-1.5 h-1.5 bg-white rounded-full animate-pulse [animation-delay:2500ms]"></div>
      <div class="absolute top-1/2 right-1/3 w-1 h-1 bg-white/70 rounded-full animate-pulse [animation-delay:1800ms]"></div>
    </div>

    <UContainer class="relative z-10">
      <div class="text-center max-w-3xl mx-auto scale-in-scroll">
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-extrabold text-white mb-4 sm:mb-6 drop-shadow-lg">
          {{ t('home.cta.title') }}
        </h2>
        <p class="text-lg sm:text-xl md:text-2xl text-white/95 mb-8 sm:mb-10 drop-shadow">
          {{ t('home.cta.description') }}
        </p>
        <div class="flex justify-center">
          <UButton
            @click="emit('start')"
            color="neutral"
            variant="solid"
            size="xl"
            icon="i-heroicons-rocket-launch"
            class="shadow-2xl bg-white text-indigo-600 hover:bg-gray-50 hover:scale-105 transition-all duration-300 min-w-[200px]"
          >
            {{ t('home.startButton') }}
          </UButton>
        </div>
      </div>
    </UContainer>
  </section>
</template>
