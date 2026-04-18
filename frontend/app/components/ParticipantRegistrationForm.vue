<script setup lang="ts">
import type { FormSubmitEvent } from "#ui/types";
import type { ParticipantForm, ParticipantRoleType } from "~/types/api";
import {
  createParticipantSchemas,
  type ParticipantRegistrationSchema,
} from "~/schemas/participant";
import { useNotificationsStore } from "~/stores/notifications";
import { useParticipantStore } from "~/stores/participant";

const participantStore = useParticipantStore();
const { getErrorMessage, isErrorCode } = useErrorHandler();
const { t } = useI18n();
const api = useApi();
const notifications = useNotificationsStore();

const state = reactive({
  full_name: "",
  participant_type: "" as string,
  age: null as number | null,
});

const { participantRegistrationSchema } = createParticipantSchemas(t);

// Avatar upload state
const selectedAvatar = ref<File | null>(null);
const isUploadingAvatar = ref(false);

const handleAvatarUpload = async (file: File) => {
  selectedAvatar.value = file;
};

const handleAvatarDelete = () => {
  selectedAvatar.value = null;
};

const participantTypeOptions = computed(() => [
  { value: "schoolchild", label: t("form.participantType.options.SCHOOLCHILD") },
  { value: "student", label: t("form.participantType.options.STUDENT") },
]);

const onSubmit = async (event: FormSubmitEvent<ParticipantRegistrationSchema>) => {
  const formData: ParticipantForm = {
    full_name: event.data.full_name,
    participant_type: event.data.participant_type as ParticipantRoleType,
    age: event.data.age,
  };

  await participantStore.registerParticipant(formData);

  if (participantStore.registrationSuccess && selectedAvatar.value) {
    isUploadingAvatar.value = true;
    const { error } = await api.attachAvatar(selectedAvatar.value);
    isUploadingAvatar.value = false;

    if (error) {
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
};

const apiErrorMessage = computed(() => getErrorMessage(participantStore.error));

const showProfileLink = computed(() =>
  isErrorCode(participantStore.error, "PARTICIPANT_ALREADY_EXISTS") ||
  isErrorCode(participantStore.error, "AUTH_USER_ALREADY_EXISTS"),
);

const isLoading = computed(() => participantStore.loading || isUploadingAvatar.value);
</script>

<template>
  <div class="animate-fade-in">
    <UAlert
      v-if="apiErrorMessage"
      color="error"
      variant="soft"
      :title="apiErrorMessage"
      icon="i-heroicons-exclamation-circle"
      :close-button="{
        icon: 'i-heroicons-x-mark-20-solid',
        color: 'neutral',
        variant: 'ghost',
        padded: false,
      }"
      @close="participantStore.clearError()"
      class="mb-6"
      role="alert"
    >
      <template v-if="showProfileLink" #description>
        <NuxtLink
          to="/me"
          class="text-primary-400 hover:text-primary-300 underline font-medium"
          :aria-label="t('participant.register.goToProfile')"
        >
          {{ t("participant.register.goToProfile") }}
        </NuxtLink>
      </template>
    </UAlert>

    <UForm
      :schema="participantRegistrationSchema"
      :state="(state as any)"
      @submit="onSubmit"
      :validate-on="['input', 'change']"
      class="space-y-5 w-full"
    >
      <!-- Avatar Upload Section -->
      <div class="flex justify-center py-2">
        <AvatarUpload
          :loading="isUploadingAvatar"
          :show-delete="!!selectedAvatar"
          @upload="handleAvatarUpload"
          @delete="handleAvatarDelete"
        />
      </div>

      <!-- Full Name -->
      <UFormField :label="t('form.fullName.label')" name="full_name" required class="w-full">
        <UInput
          v-model="state.full_name"
          :placeholder="t('form.fullName.placeholder')"
          icon="i-heroicons-user"
          size="xl"
          :maxlength="70"
          class="w-full"
        />
      </UFormField>

      <!-- Age -->
      <UFormField :label="t('form.age.label')" name="age" required class="w-full">
        <UInput
          v-model.number="state.age"
          :placeholder="t('form.age.placeholder')"
          type="number"
          size="xl"
          class="w-full"
        />
      </UFormField>

      <!-- Participant Type -->
      <UFormField :label="t('form.participantType.label')" name="participant_type" required class="w-full">
        <URadioGroup
          v-model="state.participant_type"
          :items="participantTypeOptions"
          value-key="value"
          orientation="horizontal"
          size="xl"
        />
      </UFormField>

      <div class="pt-2">
        <UButton
          type="submit"
          :loading="isLoading"
          :disabled="isLoading"
          block
          size="xl"
          icon="i-heroicons-check-circle"
          :trailing="false"
        >
          {{
            isLoading
              ? t("form.submitButton.registering")
              : t("form.submitButton.register")
          }}
        </UButton>

        <div class="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400 justify-center mt-3">
          <UIcon name="i-heroicons-shield-check" />
          <span>{{ t("form.dataProtection") }}</span>
        </div>
      </div>
    </UForm>
  </div>
</template>
