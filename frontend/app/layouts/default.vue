<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui';
import { useBlockedAccount } from "~/composables/useBlockedAccount";

const { t } = useI18n();
const { isAuthenticated, hasProfile, login, logout: handleLogout } = useAuth();
const { isAccountBlocked } = useBlockedAccount();
const userStore = useUserStore();

// Brand link destination depends on auth state
const brandLink = computed(() => {
  return isAuthenticated.value && hasProfile.value ? '/me' : '/';
});

// Show avatar for authenticated users with profile
const showAvatar = computed(() => isAuthenticated.value && hasProfile.value);

// Public "browse" link — shown to anon, organizers, admins. Participants get
// the /explore variant instead (see participant branch below).
const browseNavItem = computed<NavigationMenuItem>(() => ({
  label: t('nav.browseCompetitions'),
  icon: 'i-heroicons-magnifying-glass',
  to: '/competitions',
}));

// Navigation items
const navItems = computed<NavigationMenuItem[]>(() => {
  if (!isAuthenticated.value || !hasProfile.value) {
    return [browseNavItem.value];
  }

  const items: NavigationMenuItem[] = [];

  // Participants get /explore instead of /competitions; everyone else sees the
  // public browse link.
  if (userStore.isParticipant) {
    items.push({
      label: t('nav.explore'),
      icon: 'i-heroicons-sparkles',
      to: '/explore',
    });
    items.push({
      label: t('nav.myApplications'),
      icon: 'i-heroicons-inbox-stack',
      to: '/me/applications',
    });
  } else {
    items.push(browseNavItem.value);
  }

  if (userStore.isAdmin) {
    items.push({
      label: t('nav.adminPanel'),
      icon: 'i-heroicons-shield-check',
      to: '/admin/users',
      children: [
        { label: t('admin.users.nav'), icon: 'i-heroicons-users', to: '/admin/users' },
        { label: t('admin.invites.nav'), icon: 'i-heroicons-ticket', to: '/admin/invites' },
      ],
    });
  }

  if (userStore.isOrganizer) {
    items.push({
      label: t('nav.myCompetitions'),
      icon: 'i-heroicons-trophy',
      children: [
        { label: t('nav.competitions'), icon: 'i-heroicons-list-bullet', to: '/me/competitions' },
        { label: t('nav.applicationForms'), icon: 'i-heroicons-document-text', to: '/me/competitions/application-form' },
      ],
    });
    items.push({
      label: t('nav.applications'),
      icon: 'i-heroicons-users',
      to: '/me/competitions/applications',
    });
  }

  return items;
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
            class="h-10 w-10 sm:h-12 sm:w-12 md:h-14 md:w-14 lg:h-16 lg:w-16 object-contain transition-transform group-hover:scale-110" />
          <span
            class="text-lg sm:text-xl font-extrabold text-gray-900 dark:text-gray-100 group-hover:text-primary-500 dark:group-hover:text-primary-400 transition-colors">
            {{ t("nav.brand") }}
          </span>
        </NuxtLink>
      </template>

      <template #default>
        <!-- Navigation for organizers -->
        <UNavigationMenu :items="navItems" variant="link" class="hidden md:flex" />
      </template>

      <template #right>
        <!-- Show avatar for authenticated users -->
        <template v-if="isAccountBlocked">
          <UButton
            @click="handleLogout"
            color="neutral"
            variant="ghost"
            size="md"
            icon="i-heroicons-arrow-right-on-rectangle"
            square
            :aria-label="t('nav.logout')"
          />
        </template>
        <template v-else-if="showAvatar">
          <NotificationBell />
          <NuxtLink to="/me" :aria-label="t('nav.profile')">
            <UAvatar
              :src="userStore.profile?.avatar_url || '/no-photo.png'"
              :alt="userStore.organizer?.organizer_name || t('profile.userBadge')"
              size="md"
              class="hover:ring-2 hover:ring-primary-500 transition-all cursor-pointer"
            />
          </NuxtLink>
          <UButton
            @click="handleLogout"
            color="neutral"
            variant="ghost"
            size="md"
            icon="i-heroicons-arrow-right-on-rectangle"
            square
            :aria-label="t('nav.logout')"
            class="hidden md:flex"
          />
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
              <div class="p-4 space-y-4 w-[min(18rem,calc(100vw-2rem))]">
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
        <!-- Mobile menu -->
        <UNavigationMenu :items="navItems" orientation="vertical" class="-mx-2.5" />
        <USeparator class="my-2" />
        <div class="flex items-center justify-between px-2.5 py-2">
          <span class="text-sm font-medium text-default">{{ t('nav.theme') }}</span>
          <ThemeToggle size="sm" />
        </div>
        <div class="flex items-center justify-between px-2.5 py-2">
          <span class="text-sm font-medium text-default">{{ t('nav.language') }}</span>
          <LanguageSwitcher size="sm" />
        </div>
      </template>
    </UHeader>

    <UMain>
      <slot />
    </UMain>

    <!-- Footer -->
    <footer class="bg-gray-100 dark:bg-gray-950 border-t border-gray-200 dark:border-gray-800">
      <UContainer class="py-12">
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 sm:gap-8">
          <!-- Brand Section -->
          <div class="space-y-4">
            <div class="flex items-center gap-3">
              <img src="/logo.png" alt="DreamTeams Logo" class="h-10 w-10 object-contain" />
              <span class="text-xl font-bold bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
                {{ t("nav.brand") }}
              </span>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-300 leading-relaxed max-w-xs">
              {{ t("footer.platformDescription") }}
            </p>
          </div>

          <!-- Links Section -->
          <div class="space-y-4">
            <h3 class="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider">
              {{ t("footer.quickLinks") }}
            </h3>
            <div class="flex flex-col gap-2">
              <NuxtLink to="/" class="text-sm text-gray-600 dark:text-gray-300 hover:text-primary-400 transition-colors">
                {{ t("nav.home") }}
              </NuxtLink>
              <NuxtLink to="/legal/terms-of-service" class="text-sm text-gray-600 dark:text-gray-300 hover:text-primary-400 transition-colors">
                {{ t("footer.termsOfService") }}
              </NuxtLink>
              <NuxtLink to="/legal/privacy-policy" class="text-sm text-gray-600 dark:text-gray-300 hover:text-primary-400 transition-colors">
                {{ t("footer.privacyPolicy") }}
              </NuxtLink>
              <NuxtLink to="/legal/cookie-policy" class="text-sm text-gray-600 dark:text-gray-300 hover:text-primary-400 transition-colors">
                {{ t("footer.cookiePolicy") }}
              </NuxtLink>
              <a href="mailto:structnull@yandex.ru" class="text-sm text-gray-600 dark:text-gray-300 hover:text-primary-400 transition-colors">
                {{ t("footer.support") }}
              </a>
            </div>
          </div>

          <!-- Contact Section -->
          <div class="space-y-2">
            <h3 class="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider">
              {{ t("footer.contact") }}
            </h3>
            <a href="mailto:structnull@yandex.ru"
               class="inline-flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300 hover:text-primary-400 transition-colors">
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
