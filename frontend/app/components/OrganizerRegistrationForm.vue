<script setup lang="ts">
import type { FormSubmitEvent } from "#ui/types";
import type { OrganizerForm } from "~/types/api";
import {
  createOrganizerSchemas,
  type OrganizerRegistrationSchema,
} from "~/schemas/organizer";

import { useNotificationsStore } from "~/stores/notifications";

const organizerStore = useOrganizerStore();
const { getErrorMessage, isErrorCode } = useErrorHandler();
const { t } = useI18n();
const api = useApi();
const notifications = useNotificationsStore();

const state = reactive({
  organizer_name: "",
  phone_number: "+7",
  invite_code: "",
});

const {
  organizerRegistrationSchema
} = createOrganizerSchemas(t);

// Avatar upload state
const selectedAvatar = ref<File | null>(null);
const isUploadingAvatar = ref(false);
const avatarUploadError = ref<string | null>(null);

// Handle avatar upload
const handleAvatarUpload = async (file: File) => {
  selectedAvatar.value = file;
  avatarUploadError.value = null;
};

// Handle avatar delete
const handleAvatarDelete = () => {
  selectedAvatar.value = null;
  avatarUploadError.value = null;
};

// Form submission handler
const onSubmit = async (event: FormSubmitEvent<OrganizerRegistrationSchema>) => {
  const formData: OrganizerForm = {
    organizer_name: event.data.organizer_name,
    phone_number: event.data.phone_number,
    invite_code: event.data.invite_code,
  };

  await organizerStore.registerOrganizer(formData);

  // If registration is successful and avatar is selected, upload it
  if (organizerStore.registrationSuccess && selectedAvatar.value) {
    isUploadingAvatar.value = true;
    const { error } = await api.attachAvatar(selectedAvatar.value);
    isUploadingAvatar.value = false;

    if (error) {
      avatarUploadError.value = getErrorMessage(error);
      notifications.add({
        title: t("apiErrors." + error.code),
        color: "error",
        icon: "i-heroicons-exclamation-triangle",
      });
    } else {
      notifications.add({
        title: t("toast.avatarUploaded.title"),
        description: t("toast.avatarUploaded.description"),
        color: "success",
        icon: "i-heroicons-check-circle",
      });
    }
  }
  // Parent component (onboarding page) will handle redirect on success
};

// Error handling using centralized composable
const apiErrorMessage = computed(() => getErrorMessage(organizerStore.error));

const showProfileLink = computed(() =>
  isErrorCode(organizerStore.error, "AUTH_USER_ALREADY_EXISTS"),
);

const isLoading = computed(() => organizerStore.loading || isUploadingAvatar.value);
</script>

<template>
  <div class="animate-fade-in">
    <UAlert v-if="apiErrorMessage" color="error" variant="soft" :title="apiErrorMessage"
      icon="i-heroicons-exclamation-circle" :close-button="{
        icon: 'i-heroicons-x-mark-20-solid',
        color: 'neutral',
        variant: 'ghost',
        padded: false,
      }" @close="organizerStore.clearError()" class="mb-6" role="alert">
      <template v-if="showProfileLink" #description>
        <NuxtLink to="/me" class="text-primary-400 hover:text-primary-300 underline font-medium"
          :aria-label="t('register.goToProfile')">
          {{ t("register.goToProfile") }}
        </NuxtLink>
      </template>
    </UAlert>

    <UForm :schema="organizerRegistrationSchema" :state="state" @submit="onSubmit"
      :validate-on="['input', 'change']"
      class="space-y-5 w-full">
      <!-- Avatar Upload Section -->
      <div class="flex justify-center py-2">
        <AvatarUpload
          :loading="isUploadingAvatar"
          :show-delete="!!selectedAvatar"
          @upload="handleAvatarUpload"
          @delete="handleAvatarDelete"
        />
      </div>

      <UFormField :label="t('form.organizerName.label')" name="organizer_name" required :aria-required="true"
        class="w-full">
        <UInput v-model="state.organizer_name" :placeholder="t('form.organizerName.placeholder')"
          icon="i-heroicons-building-office" size="xl" :maxlength="70" :aria-label="t('form.organizerName.label')"
          class="w-full" />
      </UFormField>

      <UFormField :label="t('form.phoneNumber.label')" name="phone_number" required :aria-required="true"
        class="w-full">
        <UInput v-model="state.phone_number" :placeholder="t('form.phoneNumber.placeholder')" icon="i-heroicons-phone"
          size="xl" type="tel" :aria-label="t('form.phoneNumber.label')" class="w-full" />
        <p class="mt-1 text-xs text-muted">
          {{ t("form.phoneNumber.hint") }}
        </p>
      </UFormField>

      <UFormField name="invite_code" required class="w-full">
        <template #label>
          <span class="flex items-center gap-1">
            {{ t('form.inviteCode.label') }}
            <UTooltip :text="t('form.inviteCode.hint')">
              <UIcon name="i-heroicons-question-mark-circle" class="text-gray-400 size-4 cursor-help" />
            </UTooltip>
          </span>
        </template>
        <UInput v-model="state.invite_code" :placeholder="t('form.inviteCode.placeholder')"
          icon="i-heroicons-key" size="xl" :aria-label="t('form.inviteCode.label')" class="w-full" />
      </UFormField>

      <div class="pt-2">
        <UButton type="submit" :loading="isLoading" :disabled="isLoading"
          :aria-busy="isLoading" block size="xl" icon="i-heroicons-check-circle" :trailing="false">
          {{
            isLoading
              ? t("form.submitButton.registering")
              : t("form.submitButton.register")
          }}
        </UButton>

        <div class="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400 justify-center mt-3" role="note">
          <UIcon name="i-heroicons-shield-check" aria-hidden="true" />
          <span>{{ t("form.dataProtection") }}</span>
        </div>
      </div>
    </UForm>
  </div>
</template>
