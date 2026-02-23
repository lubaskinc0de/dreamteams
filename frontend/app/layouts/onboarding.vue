<script setup lang="ts">
const { t } = useI18n();
const { isLoading } = useAuth();
const isSettingsOpen = ref(false);
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
    <UHeader :ui="{ toggle: 'hidden', center: 'flex' }">
      <!-- Spacer mirrors the settings button width to keep the brand centered -->
      <template #left>
        <div class="w-10 h-10" aria-hidden="true" />
      </template>

      <!-- Center: brand title -->
      <span class="text-xl font-bold text-gray-900 dark:text-gray-100">
        {{ t("nav.brand") }}
      </span>

      <template #right>
        <UPopover v-model:open="isSettingsOpen" :ui="{ content: 'p-3 min-w-[180px]' }">
          <UButton
            icon="i-heroicons-cog-6-tooth"
            color="neutral"
            variant="ghost"
            size="lg"
            :aria-label="t('nav.settings')"
          />
          <template #content>
            <div class="flex flex-col gap-3">
              <div class="flex items-center justify-between gap-3">
                <span class="text-sm text-gray-700 dark:text-gray-300">{{ t('theme.toggle') }}</span>
                <ThemeToggle />
              </div>
              <USeparator />
              <div class="flex items-center justify-between gap-3">
                <span class="text-sm text-gray-700 dark:text-gray-300">{{ t('nav.language') }}</span>
                <LanguageSwitcher />
              </div>
            </div>
          </template>
        </UPopover>
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
