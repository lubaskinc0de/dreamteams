<script setup lang="ts">
/**
 * Final call-to-action section
 */

const { t } = useI18n();
</script>

<template>
  <section class="relative py-16 sm:py-20 md:py-24 overflow-hidden">
    <!-- Background with pattern (same style as Features section) -->
    <div class="absolute inset-0 bg-gradient-to-br from-primary-50/50 via-white to-white dark:from-gray-900 dark:via-gray-800 dark:to-gray-900"></div>
    <div class="absolute inset-0 opacity-[0.03] dark:opacity-[0.05]" style="background-image: url('data:image/svg+xml,%3Csvg width=&quot;60&quot; height=&quot;60&quot; viewBox=&quot;0 0 60 60&quot; xmlns=&quot;http://www.w3.org/2000/svg&quot;%3E%3Cg fill=&quot;none&quot; fill-rule=&quot;evenodd&quot;%3E%3Cg fill=&quot;%239C92AC&quot; fill-opacity=&quot;1&quot;%3E%3Cpath d=&quot;M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z&quot;/%3E%3C/g%3E%3C/g%3E%3C/svg%3E');"></div>

    <UContainer class="relative z-10">
      <div class="text-center max-w-3xl mx-auto scale-in-scroll">
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-extrabold mb-4 sm:mb-6">
          <span class="text-primary-600 dark:text-primary-400">
            {{ t('home.cta.title') }}
          </span>
        </h2>
        <p class="text-lg sm:text-xl md:text-2xl text-gray-600 dark:text-gray-400 mb-8 sm:mb-10">
          {{ t('home.cta.description') }}
        </p>
        <div class="flex justify-center">
          <UButton
            @click="navigateTo('/competitions')"
            color="primary"
            variant="solid"
            size="xl"
            icon="i-heroicons-magnifying-glass"
            class="shadow-xl hover:scale-105 transition-all duration-300 min-w-[200px]"
            :ui="{ base: 'justify-center' }"
          >
            {{ t('home.findHackathonButton') }}
          </UButton>
        </div>
      </div>
    </UContainer>
  </section>
</template>
