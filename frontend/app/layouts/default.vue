<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui';

const { t } = useI18n();
const { isAuthenticated, hasProfile, login } = useAuth();
const userStore = useUserStore();

// Brand link destination depends on auth state
const brandLink = computed(() => {
  return isAuthenticated.value && hasProfile.value ? '/me' : '/';
});

// Show avatar for authenticated users with profile
const showAvatar = computed(() => isAuthenticated.value && hasProfile.value);

// Navigation items for organizers
const navItems = computed<NavigationMenuItem[]>(() => {
  if (!isAuthenticated.value || !hasProfile.value || !userStore.isOrganizer) {
    return [];
  }

  return [
    {
      label: t('nav.competitions'),
      icon: 'i-heroicons-trophy',
      to: '/competitions',
    },
  ];
});

// Handle login
const handleLogin = async () => {
  await login();
};
</script>

<template>
  <!-- Main Layout -->
  <div class="min-h-screen bg-white dark:bg-gray-900 flex flex-col">
    <UHeader>
      <template #left>
        <NuxtLink :to="brandLink" class="flex items-center gap-3 group" :aria-label="t('nav.brand')">
          <img src="/logo.png" alt="DreamTeams Logo"
            class="h-16 w-16 object-contain transition-transform group-hover:scale-110" />
          <div class="hidden sm:block">
            <span
              class="text-xl font-bold text-gray-900 dark:text-gray-100 group-hover:text-primary-500 dark:group-hover:text-primary-400 transition-colors">
              {{ t("nav.brand") }}
            </span>
            <span class="block text-xs text-gray-600 dark:text-gray-400">{{
              t("nav.brandSubtitle")
            }}</span>
          </div>
        </NuxtLink>
      </template>

      <template #default>
        <!-- Navigation for organizers -->
        <UNavigationMenu v-if="navItems.length > 0" :items="navItems" variant="link" class="hidden md:flex" />
      </template>

      <template #right>
        <!-- Show avatar for authenticated users -->
        <template v-if="showAvatar">
          <NuxtLink to="/me" :aria-label="t('nav.profile')">
            <UAvatar :src="userStore.organizer?.logo || undefined"
              :alt="userStore.organizer?.organizer_name || t('profile.userBadge')" size="md"
              class="hover:ring-2 hover:ring-primary-500 transition-all cursor-pointer" />
          </NuxtLink>
        </template>
        <!-- Login button and settings menu for unauthenticated users -->
        <template v-else>
          <UButton
            @click="handleLogin"
            color="primary"
            variant="solid"
            size="md"
            :label="t('nav.login')"
            icon="i-heroicons-arrow-right-on-rectangle"
          />
          <UPopover>
            <UButton
              color="neutral"
              variant="ghost"
              size="md"
              icon="i-heroicons-cog-6-tooth"
              square
              :aria-label="t('nav.settings')"
            />
            <template #content>
              <div class="p-4 space-y-4 min-w-48">
                <div class="flex items-center justify-between gap-4">
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ t('nav.theme') }}
                  </span>
                  <ThemeToggle size="md" />
                </div>
                <USeparator />
                <div class="flex items-center justify-between gap-4">
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ t('nav.language') }}
                  </span>
                  <LanguageSwitcher size="md" />
                </div>
              </div>
            </template>
          </UPopover>
        </template>
      </template>

      <template #body>
        <!-- Mobile menu content -->
        <UNavigationMenu v-if="navItems.length > 0" :items="navItems" orientation="vertical" class="-mx-2.5" />

        <USeparator v-if="navItems.length > 0" class="my-4" />

        <!-- Mobile menu footer with controls -->
        <div v-if="showAvatar" class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-3">
            <ThemeToggle size="lg" />
            <LanguageSwitcher size="lg" />
          </div>

          <NuxtLink to="/me" :aria-label="t('nav.profile')">
            <UAvatar :src="userStore.organizer?.logo || undefined"
              :alt="userStore.organizer?.organizer_name || t('profile.userBadge')" size="md"
              class="hover:ring-2 hover:ring-primary-500 transition-all cursor-pointer" />
          </NuxtLink>
        </div>

        <!-- Mobile menu for unauthenticated users -->
        <div v-else class="space-y-4">
          <UButton
            @click="handleLogin"
            color="primary"
            variant="solid"
            size="lg"
            :label="t('nav.login')"
            icon="i-heroicons-arrow-right-on-rectangle"
            block
          />
          <div class="flex items-center justify-between gap-4">
            <div class="flex items-center gap-3">
              <ThemeToggle size="lg" />
              <LanguageSwitcher size="lg" />
            </div>
          </div>
        </div>
      </template>
    </UHeader>

    <UMain>
      <slot />
    </UMain>

    <UFooter class="mt-0 pt-0">
      <template #left>
        <div class="flex items-center gap-3">
          <img src="/logo.png" alt="DreamTeams Logo" class="h-14 w-14 object-contain" />
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
          <UButton icon="i-heroicons-envelope" variant="ghost" size="xs" color="neutral"
            to="mailto:structnull@yandex.ru" :aria-label="t('footer.support')">
            {{ t("footer.support") }}
          </UButton>
        </div>
      </template>
    </UFooter>
  </div>
</template>