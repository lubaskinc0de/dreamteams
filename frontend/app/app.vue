<script setup lang="ts">
/**
 * Root App component
 * Wraps the entire application with UApp for global configurations
 * Provides Toast notifications, color mode, and i18n support
 */

const { isLoading: authLoading } = useAuth();

// SEO Configuration for the app
useHead({
  titleTemplate: "%s - DreamTeams",
  meta: [
    { charset: "utf-8" },
    { name: "viewport", content: "width=device-width, initial-scale=1" },
    { name: "theme-color", content: "#3b82f6" },
  ],
  link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
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
  <UApp :toaster="toaster">
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
  </UApp>
</template>
