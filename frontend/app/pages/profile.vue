<script setup lang="ts">
const userStore = useUserStore();
const { navigateTo } = useNavigation();
const { getErrorMessage } = useErrorHandler();
const { t } = useI18n();

// SEO Meta tags
useSeoMeta({
  title: t("seo.profile.title"),
  description: t("seo.profile.description"),
});

// Error message using centralized error handler
const errorMessage = computed(() => getErrorMessage(userStore.error));

const goToRegistration = () => {
  navigateTo("/register");
};
</script>

<template>
  <UPage>
    <div class="max-w-4xl mx-auto">
      <UPageHeader
        :title="t('profile.title')"
        :description="t('profile.description')"
        :headline="t('profile.headline')"
      />
    </div>

    <UPageBody>
      <div class="max-w-4xl mx-auto">
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
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
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

              <USeparator class="my-6" />

              <div
                class="bg-success-500/10 border border-success-500/20 rounded-lg p-4"
                role="status"
              >
                <div class="flex items-start gap-3">
                  <div
                    class="p-1.5 rounded-lg bg-success-500/20 mt-0.5"
                    aria-hidden="true"
                  >
                    <UIcon
                      name="i-heroicons-check-circle"
                      class="text-success-400 text-xl"
                    />
                  </div>
                  <div>
                    <h4 class="font-semibold text-success-300 mb-1">
                      {{ t("profile.registered.title") }}
                    </h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400">
                      {{ t("profile.registered.description") }}
                    </p>
                  </div>
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
        </div>
      </div>
    </UPageBody>
  </UPage>
</template>
