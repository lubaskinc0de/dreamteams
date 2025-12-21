<script setup lang="ts">
const route = useRoute();
const { t } = useI18n();
const { isAuthenticated, isLoading, login } = useAuth();

const isMenuOpen = ref(false);

const isActive = (path: string) => {
  return route.path === path;
};

const closeMenu = () => {
  isMenuOpen.value = false;
};

// Navigation links that depend on auth state
const navLinks = computed(() => {
  if (!isAuthenticated.value) {
    return [
      {
        label: t("nav.home"),
        icon: "i-heroicons-home",
        to: "/",
      },
    ];
  }

  return [
    {
      label: t("nav.home"),
      icon: "i-heroicons-home",
      to: "/",
    },
    {
      label: t("nav.profile"),
      icon: "i-heroicons-user",
      to: "/profile",
    },
    {
      label: t("nav.register"),
      icon: "i-heroicons-user-plus",
      to: "/register",
    },
  ];
});
</script>

<template>
  <div class="min-h-screen bg-white dark:bg-gray-900 flex flex-col">
    <header
      class="bg-gray-100/90 dark:bg-gray-800/90 backdrop-blur-md border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-50 shadow-lg"
      role="banner"
    >
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <NuxtLink
            to="/"
            class="flex items-center gap-3 group"
            :aria-label="t('nav.brand')"
          >
            <div
              class="p-2 rounded-lg bg-primary-500/10 group-hover:bg-primary-500/20 transition-colors"
              aria-hidden="true"
            >
              <UIcon
                name="i-heroicons-trophy"
                class="text-2xl text-primary-500"
              />
            </div>
            <div class="hidden sm:block">
              <span
                class="text-xl font-bold text-gray-900 dark:text-gray-100 group-hover:text-primary-500 dark:group-hover:text-primary-400 transition-colors"
              >
                {{ t("nav.brand") }}
              </span>
              <span class="block text-xs text-gray-600 dark:text-gray-400">{{
                t("nav.brandSubtitle")
              }}</span>
            </div>
          </NuxtLink>

          <!-- Desktop Navigation -->
          <nav
            class="hidden md:flex gap-2 items-center"
            role="navigation"
            aria-label="Main navigation"
          >
            <!-- Login Button (shown only when not authenticated) -->
            <UButton
              v-if="!isLoading && !isAuthenticated"
              @click="login"
              color="primary"
              variant="solid"
              icon="i-heroicons-arrow-right-on-rectangle"
              size="lg"
              :aria-label="t('nav.login')"
            >
              {{ t('nav.login') }}
            </UButton>

            <!-- Authenticated Navigation -->
            <template v-else-if="isAuthenticated">
              <UButton
                v-for="link in navLinks"
                :key="link.to"
                :to="link.to"
                :color="isActive(link.to) ? 'primary' : 'neutral'"
                :variant="isActive(link.to) ? 'soft' : 'ghost'"
                :icon="link.icon"
                size="lg"
                :aria-current="isActive(link.to) ? 'page' : undefined"
              >
                {{ link.label }}
              </UButton>
            </template>

            <!-- Theme Toggle -->
            <ThemeToggle size="lg" />

            <!-- Language Switcher -->
            <LanguageSwitcher size="lg" />
          </nav>

          <!-- Mobile Menu Button & Utils -->
          <div class="flex md:hidden items-center gap-2">
            <ThemeToggle size="lg" />
            <LanguageSwitcher size="lg" />

            <UButton
              :icon="isMenuOpen ? 'i-heroicons-x-mark' : 'i-heroicons-bars-3'"
              color="neutral"
              variant="ghost"
              size="lg"
              @click="isMenuOpen = !isMenuOpen"
              :aria-label="isMenuOpen ? 'Close menu' : 'Open menu'"
              :aria-expanded="isMenuOpen"
            />
          </div>
        </div>

        <!-- Mobile Menu Dropdown -->
        <Transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="opacity-0 -translate-y-2"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-2"
        >
          <div
            v-if="isMenuOpen"
            class="md:hidden pb-4 space-y-2"
          >
            <!-- Login Button for Mobile -->
            <UButton
              v-if="!isLoading && !isAuthenticated"
              @click="login(); closeMenu()"
              color="primary"
              variant="solid"
              icon="i-heroicons-arrow-right-on-rectangle"
              size="lg"
              block
              :aria-label="t('nav.login')"
            >
              {{ t('nav.login') }}
            </UButton>

            <!-- Authenticated Mobile Navigation -->
            <template v-else-if="isAuthenticated">
              <UButton
                v-for="link in navLinks"
                :key="link.to"
                :to="link.to"
                :color="isActive(link.to) ? 'primary' : 'neutral'"
                :variant="isActive(link.to) ? 'soft' : 'ghost'"
                :icon="link.icon"
                size="lg"
                block
                @click="closeMenu"
                :aria-current="isActive(link.to) ? 'page' : undefined"
              >
                {{ link.label }}
              </UButton>
            </template>
          </div>
        </Transition>
      </div>
    </header>

    <main class="flex-1 py-8" role="main">
      <slot />
    </main>

    <footer
      class="bg-gray-100 dark:bg-gray-800 border-t border-gray-200/50 dark:border-gray-700/50 mt-auto"
      role="contentinfo"
    >
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div
          class="flex flex-col md:flex-row items-center justify-between gap-4"
        >
          <div class="flex items-center gap-3">
            <div class="p-2 rounded-lg bg-primary-500/10" aria-hidden="true">
              <UIcon
                name="i-heroicons-trophy"
                class="text-xl text-primary-500"
              />
            </div>
            <div>
              <p class="font-semibold text-gray-900 dark:text-gray-100">
                {{ t("footer.platformName") }}
              </p>
              <p class="text-xs text-gray-600 dark:text-gray-400">
                {{ t("footer.platformDescription") }}
              </p>
            </div>
          </div>

          <div class="flex flex-col items-center md:items-end gap-2">
            <div class="flex items-center gap-2">
              <UBadge color="success" variant="subtle" size="xs">
                {{ t("footer.version") }}
              </UBadge>
              <span class="text-xs text-gray-600 dark:text-gray-500">{{
                t("footer.copyright")
              }}</span>
            </div>
            <div class="flex gap-3">
              <UButton
                icon="i-heroicons-envelope"
                variant="ghost"
                size="xs"
                color="neutral"
                to="mailto:support@posutochnik.ru"
                :aria-label="t('footer.support')"
              >
                {{ t("footer.support") }}
              </UButton>
              <UButton
                icon="i-heroicons-document-text"
                variant="ghost"
                size="xs"
                color="neutral"
                :aria-label="t('footer.documentation')"
              >
                {{ t("footer.documentation") }}
              </UButton>
            </div>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>
