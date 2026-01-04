<script setup lang="ts">
const { t } = useI18n();
const { isLoading } = useAuth();
</script>

<template>
  <!-- Loading State - Fullscreen spinner without header/footer -->
  <div v-if="isLoading" class="fixed inset-0 bg-white dark:bg-gray-900 flex items-center justify-center z-[9999]">
    <div class="text-center">
      <UIcon name="i-heroicons-arrow-path" class="text-5xl text-primary-500 animate-spin" />
    </div>
  </div>

  <!-- Main Layout -->
  <div v-show="!isLoading" class="min-h-screen bg-white dark:bg-gray-900 flex flex-col">
    <UHeader>
      <template #left>
        <ThemeToggle size="lg" />
      </template>

      <template #title>
        <div class="flex items-center gap-3">
          <img
            src="/logo.png"
            alt="DreamTeams Logo"
            class="h-16 w-16 object-contain"
          />
          <div>
            <span class="text-xl font-bold text-gray-900 dark:text-gray-100 block">
              {{ t("nav.brand") }}
            </span>
            <span class="text-xs text-gray-600 dark:text-gray-400 hidden sm:block">
              {{ t("nav.brandSubtitle") }}
            </span>
          </div>
        </div>
      </template>

      <template #right>
        <LanguageSwitcher size="lg" />
      </template>
    </UHeader>

    <main class="flex-1 py-8" role="main">
      <slot />
    </main>

    <UFooter class="mt-0 pt-0">
      <template #left>
        <div class="flex items-center gap-3">
          <img
            src="/logo.png"
            alt="DreamTeams Logo"
            class="h-14 w-14 object-contain"
          />
          <div>
            <p class="font-semibold text-gray-900 dark:text-gray-100">
              {{ t("footer.platformName") }}
            </p>
            <p class="text-xs text-gray-600 dark:text-gray-400">
              {{ t("footer.platformDescription") }}
            </p>
          </div>
        </div>
      </template>

      <template #right>
        <div class="flex flex-col items-center md:items-end gap-2">
          <span class="text-xs text-gray-600 dark:text-gray-500">{{
            t("footer.copyright")
          }}</span>
        </div>
      </template>
    </UFooter>
  </div>
</template>
