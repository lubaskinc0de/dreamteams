<script setup lang="ts">
import type { FormSubmitEvent } from "#ui/types";
import type { ParticipantForm, ParticipantRoleType } from "~/types/api";
import {
  createParticipantSchemas,
  type ParticipantRegistrationSchema,
} from "~/schemas/participant";
import { useParticipantStore } from "~/stores/participant";

const participantStore = useParticipantStore();
const { getErrorMessage, isErrorCode } = useErrorHandler();
const { t } = useI18n();

const state = reactive({
  full_name: "",
  participant_type: "" as string,
  age: null as number | null,
  privacy_consent: false,
  terms_consent: false,
});

const { participantRegistrationSchema } = createParticipantSchemas(t);

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
  // Avatar is managed on the profile page after registration completes.
};

const apiErrorMessage = computed(() => getErrorMessage(participantStore.error));

const showProfileLink = computed(() =>
  isErrorCode(participantStore.error, "PARTICIPANT_ALREADY_EXISTS") ||
  isErrorCode(participantStore.error, "AUTH_USER_ALREADY_EXISTS"),
);

const isLoading = computed(() => participantStore.loading);
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
          :min="1"
          :step="1"
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

      <UFormField name="privacy_consent" required class="w-full">
        <UCheckbox v-model="state.privacy_consent" :aria-label="t('form.privacyConsent.label')">
          <template #label>
            <span class="text-sm text-gray-700 dark:text-gray-300">
              {{ t('form.privacyConsent.label') }}
              <NuxtLink to="/legal/privacy-policy" target="_blank"
                class="text-primary-500 hover:text-primary-400 underline">
                {{ t('form.privacyConsent.link') }}
              </NuxtLink>
            </span>
          </template>
        </UCheckbox>
      </UFormField>

      <UFormField name="terms_consent" required class="w-full">
        <UCheckbox v-model="state.terms_consent" :aria-label="t('form.termsConsent.label')">
          <template #label>
            <span class="text-sm text-gray-700 dark:text-gray-300">
              {{ t('form.termsConsent.label') }}
              <NuxtLink to="/legal/terms-of-service" target="_blank"
                class="text-primary-500 hover:text-primary-400 underline">
                {{ t('form.termsConsent.link') }}
              </NuxtLink>
            </span>
          </template>
        </UCheckbox>
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
      </div>
    </UForm>
  </div>
</template>
