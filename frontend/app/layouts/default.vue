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
            class="h-12 w-12 sm:h-16 sm:w-16 object-contain transition-transform group-hover:scale-110" />
          <span
            class="text-lg sm:text-xl font-extrabold text-gray-900 dark:text-gray-100 group-hover:text-primary-500 dark:group-hover:text-primary-400 transition-colors">
            {{ t("nav.brand") }}
          </span>
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
            <UAvatar
              :src="userStore.profile?.avatar_url || undefined"
              :alt="userStore.organizer?.organizer_name || t('profile.userBadge')"
              size="md"
              class="hover:ring-2 hover:ring-primary-500 transition-all cursor-pointer"
            />
          </NuxtLink>
        </template>
        <!-- Login button (desktop only) and settings menu for unauthenticated users -->
        <template v-else>
          <UButton
            @click="handleLogin"
            color="primary"
            variant="solid"
            size="md"
            :label="t('nav.login')"
            icon="i-heroicons-arrow-right-on-rectangle"
            class="hidden md:flex"
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
        <!-- Mobile menu for authenticated organizers -->
        <template v-if="showAvatar && navItems.length > 0">
          <UNavigationMenu :items="navItems" orientation="vertical" class="-mx-2.5" />
        </template>
      </template>
    </UHeader>

    <UMain>
      <slot />
    </UMain>

    <!-- Footer -->
    <footer class="bg-gray-900 dark:bg-gray-950 border-t border-gray-800">
      <UContainer class="py-12">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <!-- Brand Section -->
          <div class="space-y-4">
            <div class="flex items-center gap-3">
              <img src="/logo.png" alt="DreamTeams Logo" class="h-10 w-10 object-contain" />
              <span class="text-xl font-bold bg-gradient-to-r from-primary-400 to-success-400 bg-clip-text text-transparent">
                {{ t("nav.brand") }}
              </span>
            </div>
            <p class="text-sm text-gray-400 leading-relaxed max-w-xs">
              {{ t("footer.platformDescription") }}
            </p>
          </div>

          <!-- Links Section -->
          <div class="space-y-4">
            <h3 class="text-sm font-semibold text-white uppercase tracking-wider">
              {{ t("footer.quickLinks") }}
            </h3>
            <div class="flex flex-col gap-2">
              <NuxtLink to="/" class="text-sm text-gray-400 hover:text-primary-400 transition-colors">
                {{ t("nav.home") }}
              </NuxtLink>
              <a href="mailto:structnull@yandex.ru" class="text-sm text-gray-400 hover:text-primary-400 transition-colors">
                {{ t("footer.support") }}
              </a>
            </div>
          </div>

          <!-- Contact Section -->
          <div class="space-y-2">
            <h3 class="text-sm font-semibold text-white uppercase tracking-wider">
              {{ t("footer.contact") }}
            </h3>
            <a href="mailto:structnull@yandex.ru"
               class="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-primary-400 transition-colors">
              <UIcon name="i-heroicons-envelope" class="text-lg" />
              structnull@yandex.ru
            </a>
            <p class="text-sm text-gray-500 pt-2">
              {{ t("footer.copyright") }}
            </p>
          </div>
        </div>
      </UContainer>
    </footer>
  </div>
</template>