<script setup lang="ts">
const userStore = useUserStore();
const { navigateTo } = useNavigation();
const { getErrorMessage } = useErrorHandler();
const { t } = useI18n();
const config = useRuntimeConfig();

// SEO Meta tags
useSeoMeta({
  title: t("seo.profile.title"),
  description: t("seo.profile.description"),
});

// Error message using centralized error handler
const errorMessage = computed(() => getErrorMessage(userStore.error));

const goToRegistration = () => {
  navigateTo("/onboarding");
};

// Tabs configuration
const tabs = computed(() => [
  {
    label: t('profile.tabs.information'),
    icon: 'i-heroicons-user-circle',
    slot: 'information',
  },
  {
    label: t('profile.tabs.settings'),
    icon: 'i-heroicons-cog-6-tooth',
    slot: 'settings',
  },
]);

// Logout handler
const handleLogout = () => {
  window.location.href = `${config.public.apiBase}/oauth2/sign_out?rd=/`;
};
</script>

<template>
  <UPage>
    <UPageBody>
      <div class="max-w-6xl mx-auto">
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {{ t('profile.title') }}
          </h1>
          <p class="text-gray-600 dark:text-gray-400">
            {{ t('profile.description') }}
          </p>
        </div>
        <UAlert
          v-if="errorMessage"
          color="error"
          variant="soft"
          :title="errorMessage"
          icon="i-heroicons-exclamation-triangle"
          :close-button="{
            icon: 'i-heroicons-x-mark-20-solid',
            color: 'neutral',
            variant: 'ghost',
            padded: false,
          }"
          @close="userStore.clearError()"
          class="mb-6"
        />

        <!-- Skeleton Loader based on MCP documentation -->
        <div v-if="userStore.loading">
          <UCard>
            <template #header>
              <div class="flex items-center gap-4">
                <USkeleton class="h-20 w-20 rounded-full" />
                <div class="space-y-2 flex-1">
                  <USkeleton class="h-6 w-48" />
                  <USkeleton class="h-4 w-32" />
                </div>
              </div>
            </template>
            <div class="space-y-4">
              <USkeleton class="h-4 w-full" />
              <USkeleton class="h-4 w-3/4" />
              <USkeleton class="h-4 w-5/6" />
            </div>
          </UCard>
        </div>

        <div v-else-if="userStore.profile" class="animate-fade-in">
          <UTabs
            :items="tabs"
            orientation="horizontal"
            variant="pill"
            class="w-full"
          >
            <!-- Information Tab -->
            <template #information>
          <UCard>
            <template #header>
              <div class="flex items-start justify-between">
                <div class="flex items-center gap-4">
                  <UAvatar
                    :src="userStore.organizer?.logo || undefined"
                    :alt="
                      userStore.organizer?.organizer_name ||
                      t('profile.userBadge')
                    "
                    size="2xl"
                  />
                  <div>
                    <h2
                      class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-1"
                    >
                      {{
                        userStore.organizer?.organizer_name ||
                        t("profile.userBadge")
                      }}
                    </h2>
                    <div class="flex items-center gap-2">
                      <UBadge
                        v-if="userStore.isOrganizer"
                        color="success"
                        variant="subtle"
                        size="sm"
                        :aria-label="t('profile.organizerBadge')"
                      >
                        <template #leading>
                          <UIcon name="i-heroicons-check-circle" />
                        </template>
                        {{ t("profile.organizerBadge") }}
                      </UBadge>
                      <UBadge
                        v-else
                        color="neutral"
                        variant="subtle"
                        size="sm"
                        :aria-label="t('profile.userBadge')"
                      >
                        {{ t("profile.userBadge") }}
                      </UBadge>
                    </div>
                  </div>
                </div>
              </div>
            </template>

            <div v-if="userStore.isOrganizer && userStore.organizer">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-1">
                  <div
                    class="flex items-center gap-2 text-sm font-medium text-gray-600 dark:text-gray-400 mb-2"
                  >
                    <UIcon name="i-heroicons-building-office" class="text-base" />
                    <span>{{ t("profile.fields.organizerName") }}</span>
                  </div>
                  <p class="text-lg text-gray-900 dark:text-gray-100 pl-6">
                    {{ userStore.organizer.organizer_name }}
                  </p>
                </div>

                <div class="space-y-1">
                  <div
                    class="flex items-center gap-2 text-sm font-medium text-gray-600 dark:text-gray-400 mb-2"
                  >
                    <UIcon name="i-heroicons-phone" class="text-base" />
                    <span>{{ t("profile.fields.phoneNumber") }}</span>
                  </div>
                  <p class="text-lg text-gray-900 dark:text-gray-100 pl-6">
                    {{ userStore.organizer.phone_number }}
                  </p>
                </div>

                <div class="space-y-1">
                  <div
                    class="flex items-center gap-2 text-sm font-medium text-gray-600 dark:text-gray-400 mb-2"
                  >
                    <UIcon name="i-heroicons-envelope" class="text-base" />
                    <span>{{ t("profile.fields.contactEmail") }}</span>
                  </div>
                  <p class="text-lg text-gray-900 dark:text-gray-100 pl-6">
                    {{ userStore.organizer.contact_email }}
                  </p>
                </div>

                <div class="space-y-1">
                  <div
                    class="flex items-center gap-2 text-sm font-medium text-gray-600 dark:text-gray-400 mb-2"
                  >
                    <UIcon
                      name="i-heroicons-identification"
                      class="text-base"
                    />
                    <span>{{ t("profile.fields.organizerId") }}</span>
                  </div>
                  <p
                    class="text-sm text-gray-600 dark:text-gray-400 pl-6 font-mono"
                  >
                    {{ userStore.organizer.id }}
                  </p>
                </div>
              </div>
            </div>

            <div v-else>
              <UEmpty
                icon="i-heroicons-trophy"
                :title="t('profile.notRegistered.title')"
                :description="t('profile.notRegistered.description')"
              >
                <template #actions>
                  <UButton
                    size="lg"
                    icon="i-heroicons-user-plus"
                    @click="goToRegistration"
                    :aria-label="t('profile.notRegistered.button')"
                  >
                    {{ t("profile.notRegistered.button") }}
                  </UButton>
                </template>
              </UEmpty>
            </div>

            <template #footer>
              <div
                class="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-500"
              >
                <UIcon name="i-heroicons-identification" />
                <span class="font-mono"
                  >{{ t("profile.fields.userId") }}:
                  {{ userStore.profile.user_id }}</span
                >
              </div>
            </template>
          </UCard>
            </template>

            <!-- Settings Tab -->
            <template #settings>
              <UCard>
                <div class="space-y-8">
                  <!-- Appearance Section -->
                  <div>
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                      {{ t('profile.settings.appearance.title') }}
                    </h3>

                    <div class="space-y-4">
                      <div class="flex items-center justify-between">
                        <div>
                          <p class="font-medium text-gray-900 dark:text-gray-100">
                            {{ t('profile.settings.appearance.theme') }}
                          </p>
                          <p class="text-sm text-gray-600 dark:text-gray-400">
                            {{ t('profile.settings.appearance.themeDescription') }}
                          </p>
                        </div>
                        <ThemeToggle size="lg" />
                      </div>

                      <USeparator />

                      <div class="flex items-center justify-between">
                        <div>
                          <p class="font-medium text-gray-900 dark:text-gray-100">
                            {{ t('profile.settings.appearance.language') }}
                          </p>
                          <p class="text-sm text-gray-600 dark:text-gray-400">
                            {{ t('profile.settings.appearance.languageDescription') }}
                          </p>
                        </div>
                        <LanguageSwitcher size="lg" />
                      </div>
                    </div>
                  </div>

                  <USeparator />

                  <!-- Authentication Section -->
                  <div>
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                      {{ t('profile.settings.authentication.title') }}
                    </h3>

                    <UButton
                      color="error"
                      variant="soft"
                      size="lg"
                      icon="i-heroicons-arrow-right-on-rectangle"
                      @click="handleLogout"
                    >
                      {{ t('profile.settings.authentication.logout') }}
                    </UButton>
                  </div>
                </div>
              </UCard>
            </template>
          </UTabs>
        </div>
      </div>
    </UPageBody>
  </UPage>
</template>
