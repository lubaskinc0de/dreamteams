<script setup lang="ts">
import { useNotificationsStore } from "~/stores/notifications";

const userStore = useUserStore();
const { navigateTo } = useNavigation();
const { getErrorMessage } = useErrorHandler();
const { t } = useI18n();
const config = useRuntimeConfig();
const api = useApi();
const notifications = useNotificationsStore();

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

// Avatar modal state
const isAvatarModalOpen = ref(false);
const isUploadingAvatar = ref(false);

// Handle avatar upload
const handleAvatarUpload = async (file: File) => {
  isUploadingAvatar.value = true;
  const { error } = await api.attachAvatar(file);

  if (error) {
    isUploadingAvatar.value = false;
    notifications.add({
      title: t("apiErrors." + error.code),
      color: "error",
      icon: "i-heroicons-exclamation-triangle",
    });
  } else {
    // Refresh user profile to get updated avatar URL
    await userStore.fetchProfile();
    isUploadingAvatar.value = false;

    notifications.add({
      title: t("toast.avatarUploaded.title"),
      description: t("toast.avatarUploaded.description"),
      color: "success",
      icon: "i-heroicons-check-circle",
    });
    isAvatarModalOpen.value = false;
  }
};

// Handle avatar delete
const handleAvatarDelete = async () => {
  isUploadingAvatar.value = true;
  const { error } = await api.detachAvatar();

  if (error) {
    isUploadingAvatar.value = false;
    notifications.add({
      title: t("apiErrors." + error.code),
      color: "error",
      icon: "i-heroicons-exclamation-triangle",
    });
  } else {
    // Refresh user profile to clear avatar URL
    await userStore.fetchProfile();
    isUploadingAvatar.value = false;

    notifications.add({
      title: t("toast.avatarDeleted.title"),
      description: t("toast.avatarDeleted.description"),
      color: "success",
      icon: "i-heroicons-check-circle",
    });
  }
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

const isDeleteModalOpen = ref(false);
const isDeleting = ref(false);

const handleDelete = async () => {
  isDeleting.value = true;
  const result = await userStore.deleteProfile();
  isDeleting.value = false;

  if (result.success) {
    handleLogout()
  }
  isDeleteModalOpen.value = false;
};

// Logout handler
const handleLogout = () => {
  window.location.href = `${config.public.apiBase}/oauth2/sign_out?rd=/`;
};

onMounted(async () => {
  await userStore.fetchProfile();
});
</script>

<template>
  <UPage>
    <UPageBody>
      <UContainer class="!max-w-7xl">
        <UAlert v-if="errorMessage" color="error" variant="soft" :title="errorMessage"
          icon="i-heroicons-exclamation-triangle" :close-button="{
            icon: 'i-heroicons-x-mark-20-solid',
            color: 'neutral',
            variant: 'ghost',
            padded: false,
          }" @close="userStore.clearError()" class="mb-6" />

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
          <UTabs :items="tabs" orientation="horizontal" variant="pill" class="w-full">
            <!-- Information Tab -->
            <template #information>
              <UCard>
                <div class="flex flex-col lg:flex-row gap-6 lg:gap-8 items-center lg:items-start">
                  <!-- Avatar Section -->
                  <div class="flex-shrink-0">
                    <div
                      class="relative group cursor-pointer w-20 h-20"
                      @click="isAvatarModalOpen = true"
                      :title="t('avatar.clickToEdit')"
                    >
                      <UAvatar
                        :src="userStore.profile?.avatar_url || '/no-photo.png'"
                        :alt="userStore.organizer?.organizer_name || userStore.participant?.full_name || t('profile.userBadge')"
                        size="3xl"
                        :ui="{ root: 'w-full h-full' }"
                        class="ring-2 ring-gray-200 dark:ring-gray-700 transition-all group-hover:ring-primary-500"
                      />
                      <div
                        class="absolute inset-0 bg-black/50 rounded-full opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                      >
                        <UIcon
                          name="i-heroicons-camera"
                          class="text-white text-3xl"
                        />
                      </div>
                    </div>
                  </div>

                  <!-- User Info -->
                  <div class="flex-1 w-full text-center lg:text-left">
                    <div class="flex items-center justify-center lg:justify-start gap-3 mb-4 flex-wrap">
                      <h2 class="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-gray-100">
                        {{ userStore.organizer?.organizer_name || userStore.participant?.full_name || t("profile.userBadge") }}
                      </h2>
                      <UBadge
                        v-if="userStore.isAdmin"
                        color="warning"
                        variant="subtle"
                        :label="t('profile.adminBadge')"
                        icon="i-heroicons-shield-check"
                      />
                      <UBadge
                        v-else-if="userStore.isOrganizer"
                        color="primary"
                        variant="subtle"
                        :label="t('profile.organizerBadge')"
                        icon="i-heroicons-building-office"
                      />
                      <UBadge
                        v-else-if="userStore.isParticipant"
                        color="success"
                        variant="subtle"
                        :label="t('profile.participantBadge')"
                        icon="i-heroicons-user"
                      />
                    </div>

                    <!-- Organizer info -->
                    <div v-if="userStore.isOrganizer && userStore.organizer" class="space-y-2">
                      <div class="flex justify-center lg:justify-start">
                        <div class="flex items-center gap-2">
                          <UIcon name="i-heroicons-phone" class="text-lg text-gray-600 dark:text-gray-400" />
                          <p class="text-sm text-gray-900 dark:text-gray-100">{{ userStore.organizer.phone_number }}</p>
                        </div>
                      </div>
                      <div class="flex justify-center lg:justify-start">
                        <div class="flex items-center gap-2">
                          <UIcon name="i-heroicons-envelope" class="text-lg text-gray-600 dark:text-gray-400" />
                          <p class="text-sm text-gray-900 dark:text-gray-100">{{ userStore.organizer.contact_email }}</p>
                        </div>
                      </div>
                    </div>

                    <!-- Participant info -->
                    <div v-else-if="userStore.isParticipant && userStore.participant" class="space-y-4 text-left">
                      <!-- Bio -->
                      <div v-if="userStore.participant.bio">
                        <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1">
                          {{ t('profile.participant.bio') }}
                        </p>
                        <p class="text-sm text-gray-800 dark:text-gray-200">{{ userStore.participant.bio }}</p>
                      </div>

                      <!-- Experience + Domains row -->
                      <div class="flex flex-wrap gap-4">
                        <div>
                          <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1">
                            {{ t('profile.participant.experienceLevel') }}
                          </p>
                          <UBadge color="neutral" variant="subtle">
                            {{ t(`profile.participant.experienceLevels.${userStore.participant.experience_level}`) }}
                          </UBadge>
                        </div>
                        <div>
                          <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1">
                            {{ t('profile.participant.preferredDomains') }}
                          </p>
                          <div class="flex flex-wrap gap-1">
                            <UBadge
                              v-for="domain in userStore.participant.preferred_domains"
                              :key="domain"
                              color="primary"
                              variant="subtle"
                            >
                              {{ t(`profile.participant.domains.${domain}`) }}
                            </UBadge>
                          </div>
                        </div>
                      </div>

                      <!-- Skills -->
                      <div v-if="userStore.participant.skills.length">
                        <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-2">
                          {{ t('profile.participant.skills') }}
                        </p>
                        <div class="flex flex-wrap gap-2">
                          <div
                            v-for="skill in userStore.participant.skills"
                            :key="skill.name"
                            class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-gray-100 dark:bg-gray-800 text-sm"
                          >
                            <span class="font-medium text-gray-900 dark:text-gray-100">{{ skill.name }}</span>
                            <span class="text-xs text-gray-500 dark:text-gray-400">
                              {{ t(`profile.participant.skillLevels.${skill.level}`) }}
                            </span>
                          </div>
                        </div>
                      </div>

                      <!-- Contacts -->
                      <div v-if="userStore.participant.contacts.length">
                        <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-2">
                          {{ t('profile.participant.contacts') }}
                        </p>
                        <div class="flex flex-wrap gap-2">
                          <a
                            v-for="contact in userStore.participant.contacts"
                            :key="contact.title"
                            :href="contact.url"
                            target="_blank"
                            rel="noopener noreferrer"
                            class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-gray-200 dark:border-gray-700 text-sm text-primary-500 hover:text-primary-400 transition-colors"
                          >
                            <UIcon name="i-heroicons-link" class="text-xs" />
                            {{ contact.title }}
                          </a>
                        </div>
                      </div>
                    </div>

                    <!-- Admin info -->
                    <div v-else-if="userStore.isAdmin">
                      <div class="p-6 rounded-xl border border-primary-200 dark:border-primary-800 bg-primary-50/50 dark:bg-primary-950/30 text-center space-y-3">
                        <UIcon name="i-heroicons-shield-check" class="text-4xl text-primary-500" />
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{{ t('profile.adminInfo.title') }}</h3>
                        <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('profile.adminInfo.description') }}</p>
                        <UButton size="xl" icon="i-heroicons-cog-6-tooth" to="/admin/invites">
                          {{ t('nav.adminPanel') }}
                        </UButton>
                      </div>
                    </div>

                    <!-- Not registered -->
                    <div v-else>
                      <UEmpty icon="i-heroicons-trophy" :title="t('profile.notRegistered.title')"
                        :description="t('profile.notRegistered.description')">
                        <template #actions>
                          <UButton size="xl" color="primary" icon="i-heroicons-user-plus" @click="goToRegistration"
                            :aria-label="t('profile.notRegistered.button')">
                            {{ t("profile.notRegistered.button") }}
                          </UButton>
                        </template>
                      </UEmpty>
                    </div>
                  </div>
                </div>
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
                      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                        <div class="flex-1">
                          <p class="font-medium text-gray-900 dark:text-gray-100">
                            {{ t('profile.settings.appearance.theme') }}
                          </p>
                          <p class="text-sm text-gray-600 dark:text-gray-400">
                            {{ t('profile.settings.appearance.themeDescription') }}
                          </p>
                        </div>
                        <div class="shrink-0">
                          <ThemeToggle size="lg" />
                        </div>
                      </div>

                      <USeparator />

                      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                        <div class="flex-1">
                          <p class="font-medium text-gray-900 dark:text-gray-100">
                            {{ t('profile.settings.appearance.language') }}
                          </p>
                          <p class="text-sm text-gray-600 dark:text-gray-400">
                            {{ t('profile.settings.appearance.languageDescription') }}
                          </p>
                        </div>
                        <div class="shrink-0">
                          <LanguageSwitcher size="lg" />
                        </div>
                      </div>
                    </div>
                  </div>

                  <USeparator />

                  <!-- Authentication Section -->
                  <div>
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                      {{ t('profile.settings.authentication.title') }}
                    </h3>
                    <div class="flex flex-col gap-3 items-start">
                      <UButton color="warning" variant="soft" size="lg" icon="i-heroicons-arrow-right-on-rectangle"
                        @click="handleLogout" class="w-auto justify-start">
                        {{ t('profile.settings.authentication.logout') }}
                      </UButton>

                      <UButton color="error" variant="soft" size="lg" icon="i-lucide-triangle-alert"
                        @click="isDeleteModalOpen = true" class="w-auto justify-start">
                        {{ t('profile.settings.authentication.delete_profile') }}
                      </UButton>
                    </div>
                  </div>
                </div>
              </UCard>
            </template>
          </UTabs>
        </div>
      </UContainer>
      <UiConfirmDeleteModal
        v-model:open="isDeleteModalOpen"
        :title="t('profile.delete.title')"
        :description="t('profile.delete.description')"
        :confirm-label="t('common.confirm')"
        :cancel-label="t('common.cancel')"
        :is-deleting="isDeleting"
        @confirm="handleDelete"
      />

      <!-- Avatar Edit Modal -->
      <AvatarEditModal
        v-if="isAvatarModalOpen"
        v-model:open="isAvatarModalOpen"
        :current-avatar-url="userStore.profile?.avatar_url"
        @upload="handleAvatarUpload"
        @delete="handleAvatarDelete"
      />
    </UPageBody>
  </UPage>
</template>
