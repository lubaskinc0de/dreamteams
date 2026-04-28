<script setup lang="ts">
import { useNotificationsStore } from "~/stores/notifications";
import { contactHref } from "~/utils/contact";

const userStore = useUserStore();
const { navigateTo } = useNavigation();
const { getErrorMessage } = useErrorHandler();
const { t } = useI18n();
const { logout: handleLogout } = useAuth();
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

const isOrganizerEditOpen = ref(false);
const isParticipantEditOpen = ref(false);
const isNameEditOpen = ref(false);
const fieldEditOpen = ref(false);
type ParticipantEditableField = "bio" | "experience_level" | "skills" | "contacts";
const editField = ref<ParticipantEditableField>("bio");
const openFieldEdit = (field: ParticipantEditableField) => {
  editField.value = field;
  fieldEditOpen.value = true;
};

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
                <div class="flex flex-col lg:flex-row gap-4 sm:gap-6 lg:gap-8 items-center lg:items-start">
                  <!-- Avatar Section -->
                  <div class="flex-shrink-0">
                    <div
                      class="relative group cursor-pointer w-20 h-20 sm:w-24 sm:h-24 lg:w-28 lg:h-28"
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
                    <div class="flex items-center justify-center lg:justify-start gap-2 mb-4 flex-wrap">
                      <h2 class="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-gray-100">
                        {{ userStore.organizer?.organizer_name || userStore.participant?.full_name || t("profile.userBadge") }}
                      </h2>
                      <UButton
                        v-if="userStore.isParticipant"
                        icon="i-heroicons-pencil-square"
                        color="neutral"
                        variant="ghost"
                        size="xs"
                        @click="isNameEditOpen = true"
                      />
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
                    </div>

                    <!-- Organizer info -->
                    <div v-if="userStore.isOrganizer && userStore.organizer" class="space-y-2">
                      <div class="flex justify-center lg:justify-start">
                        <a
                          :href="`tel:${userStore.organizer.phone_number}`"
                          class="flex items-center gap-2 text-sm text-gray-900 dark:text-gray-100 hover:text-primary-500 dark:hover:text-primary-400 transition-colors"
                        >
                          <UIcon name="i-heroicons-phone" class="text-lg text-gray-600 dark:text-gray-400" />
                          {{ userStore.organizer.phone_number }}
                        </a>
                      </div>
                      <div v-if="userStore.organizer.contact_email" class="flex justify-center lg:justify-start">
                        <a
                          :href="`mailto:${userStore.organizer.contact_email}`"
                          class="flex items-center gap-2 text-sm text-gray-900 dark:text-gray-100 hover:text-primary-500 dark:hover:text-primary-400 transition-colors"
                        >
                          <UIcon name="i-heroicons-envelope" class="text-lg text-gray-600 dark:text-gray-400" />
                          {{ userStore.organizer.contact_email }}
                        </a>
                      </div>
                      <div class="flex justify-center lg:justify-start pt-2">
                        <UButton
                          icon="i-heroicons-pencil-square"
                          color="neutral"
                          variant="ghost"
                          size="sm"
                          @click="isOrganizerEditOpen = true"
                        >
                          {{ t("common.edit") }}
                        </UButton>
                      </div>
                    </div>

                    <!-- Participant info -->
                    <div v-else-if="userStore.isParticipant && userStore.participant" class="space-y-4 text-left">
                      <!-- + buttons for unfilled optional fields -->
                      <div class="flex flex-wrap gap-2">
                        <UButton v-if="!userStore.participant.bio" icon="i-heroicons-plus" size="xs" color="neutral" variant="outline" @click="openFieldEdit('bio')">
                          {{ t('profile.participant.bio') }}
                        </UButton>
                        <UButton v-if="!userStore.participant.experience_level" icon="i-heroicons-plus" size="xs" color="neutral" variant="outline" @click="openFieldEdit('experience_level')">
                          {{ t('profile.participant.experienceLevel') }}
                        </UButton>
                        <UButton v-if="!userStore.participant.skills.length" icon="i-heroicons-plus" size="xs" color="neutral" variant="outline" @click="openFieldEdit('skills')">
                          {{ t('profile.participant.skills') }}
                        </UButton>
                        <UButton v-if="!userStore.participant.contacts.length" icon="i-heroicons-plus" size="xs" color="neutral" variant="outline" @click="openFieldEdit('contacts')">
                          {{ t('profile.participant.contacts') }}
                        </UButton>
                      </div>

                      <!-- Bio + Experience: two columns on lg -->
                      <div
                        v-if="userStore.participant.bio || userStore.participant.experience_level"
                        class="grid grid-cols-1 lg:grid-cols-2 gap-4"
                      >
                        <!-- Bio -->
                        <div v-if="userStore.participant.bio">
                          <div class="flex items-center gap-1 mb-1">
                            <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                              {{ t('profile.participant.bio') }}
                            </p>
                            <UButton icon="i-heroicons-pencil-square" size="xs" color="neutral" variant="ghost" :padded="false" @click="openFieldEdit('bio')" />
                          </div>
                          <p class="text-sm text-gray-800 dark:text-gray-200 leading-relaxed">{{ userStore.participant.bio }}</p>
                        </div>

                        <!-- Experience -->
                        <div v-if="userStore.participant.experience_level">
                          <div class="flex items-center gap-1 mb-1">
                            <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                              {{ t('profile.participant.experienceLevel') }}
                            </p>
                            <UButton icon="i-heroicons-pencil-square" size="xs" color="neutral" variant="ghost" :padded="false" @click="openFieldEdit('experience_level')" />
                          </div>
                          <UBadge color="neutral" variant="subtle" size="md">
                            {{ t(`profile.participant.experienceLevels.${userStore.participant.experience_level}`) }}
                          </UBadge>
                        </div>
                      </div>

                      <!-- Skills -->
                      <div v-if="userStore.participant.skills.length">
                        <!-- Skills -->
                        <div class="flex items-center gap-1 mb-2">
                          <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                            {{ t('profile.participant.skills') }}
                          </p>
                          <UButton icon="i-heroicons-pencil-square" size="xs" color="neutral" variant="ghost" :padded="false" @click="openFieldEdit('skills')" />
                        </div>
                        <div class="flex flex-wrap gap-1.5">
                          <div
                            v-for="skill in userStore.participant.skills"
                            :key="skill.name"
                            class="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-gray-100 dark:bg-gray-800"
                          >
                            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ skill.name }}</span>
                            <span class="text-xs text-gray-500 dark:text-gray-400">
                              {{ t(`profile.participant.skillLevels.${skill.level}`) }}
                            </span>
                          </div>
                        </div>
                      </div>

                      <!-- Contacts (full width) -->
                      <div v-if="userStore.participant.contacts.length">
                        <div class="flex items-center gap-1 mb-2">
                          <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                            {{ t('profile.participant.contacts') }}
                          </p>
                          <UButton icon="i-heroicons-pencil-square" size="xs" color="neutral" variant="ghost" :padded="false" @click="openFieldEdit('contacts')" />
                        </div>
                        <div class="flex flex-wrap gap-2">
                          <template
                            v-for="contact in userStore.participant.contacts"
                            :key="`${contact.title}:${contact.value}`"
                          >
                            <NuxtLink
                              v-if="contactHref(contact.value)"
                              :to="contactHref(contact.value)!"
                              target="_blank"
                              rel="noopener noreferrer"
                              class="flex items-center gap-1.5 px-3 py-1 rounded-lg border border-gray-200 dark:border-gray-700 text-sm text-primary-500 hover:text-primary-400 transition-colors"
                            >
                              <UIcon name="i-heroicons-link" class="text-xs" />
                              {{ contact.title }}
                            </NuxtLink>
                            <span
                              v-else
                              class="flex items-center gap-1.5 px-3 py-1 rounded-lg border border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300"
                            >
                              <UIcon name="i-heroicons-at-symbol" class="text-xs" />
                              {{ contact.title }}: {{ contact.value }}
                            </span>
                          </template>
                        </div>
                      </div>
                    </div>

                    <!-- Admin info -->
                    <div v-else-if="userStore.isAdmin">
                      <div class="p-6 rounded-xl border border-primary-200 dark:border-primary-800 bg-primary-50/50 dark:bg-primary-950/30 text-center space-y-3">
                        <UIcon name="i-heroicons-shield-check" class="text-4xl text-primary-500" />
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{{ t('profile.adminInfo.title') }}</h3>
                        <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('profile.adminInfo.description') }}</p>
                        <UButton size="xl" icon="i-heroicons-cog-6-tooth" to="/admin/users">
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

      <!-- Organizer Edit Modal -->
      <OrganizerEditModal
        v-if="isOrganizerEditOpen && userStore.organizer"
        v-model:open="isOrganizerEditOpen"
        :organizer-name="userStore.organizer.organizer_name"
        :contact-email="userStore.organizer.contact_email"
      />

      <!-- Participant Name Edit Modal -->
      <ParticipantNameEditModal
        v-if="isNameEditOpen && userStore.participant"
        v-model:open="isNameEditOpen"
        :current-name="userStore.participant.full_name"
      />

      <!-- Participant Field Edit Modal -->
      <ParticipantFieldEditModal
        v-if="fieldEditOpen && userStore.participant"
        v-model:open="fieldEditOpen"
        :field="editField"
      />
    </UPageBody>
  </UPage>
</template>
