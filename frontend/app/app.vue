<script setup lang="ts">
/**
 * Root App component
 * Wraps the entire application with UApp for global configurations
 * Provides Toast notifications, color mode, and i18n support
 */

// SEO Configuration for the app
useHead({
  titleTemplate: "%s - Посуточник",
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
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </UApp>
</template>
