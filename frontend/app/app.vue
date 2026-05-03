<script setup lang="ts">
import * as uiLocales from '@nuxt/ui/locale';

/**
 * Root App component
 * Wraps the entire application with UApp for global configurations
 * Provides Toast notifications, color mode, and i18n support
 */

const { isLoading: authLoading } = useAuth();
const { locale } = useI18n();

// Get Nuxt UI locale based on current i18n locale
const uiLocale = computed(() => uiLocales[locale.value as keyof typeof uiLocales] || uiLocales.ru);

// Keep the browser title stable even when pages provide their own route meta.
useHead({
  title: "DreamTeams",
  titleTemplate: () => "DreamTeams",
  htmlAttrs: {
    lang: locale,
  },
});

// Toaster configuration (from MCP documentation)
const toaster = {
  position: "top-right" as const,
  duration: 5000,
  max: 3,
  expand: true,
};
</script>

<template>
  <UApp :toaster="toaster" :locale="uiLocale">
    <!-- Show loading overlay while initial auth check is in progress -->
    <div v-if="authLoading" class="fixed inset-0 z-50 flex items-center justify-center bg-white dark:bg-gray-900">
      <div class="text-center">
        <UIcon name="i-heroicons-arrow-path" class="text-6xl text-primary-500 animate-spin mb-4" />
        <p class="text-gray-600 dark:text-gray-400">Загрузка...</p>
      </div>
    </div>

    <!-- App content - always present for Nuxt static analysis -->
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>

    <CookieConsent />
  </UApp>
</template>
