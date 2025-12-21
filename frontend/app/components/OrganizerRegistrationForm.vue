<script setup lang="ts">
import type { FormSubmitEvent } from "#ui/types";
import type { OrganizerForm } from "~/types/api";
import {
  organizerRegistrationSchema,
  formatPhoneNumber,
  type OrganizerRegistrationSchema,
} from "~/schemas/organizer";

const organizerStore = useOrganizerStore();
const { navigateTo } = useNavigation();
const { getErrorMessage, isErrorCode } = useErrorHandler();
const { t } = useI18n();

const state = reactive({
  organizer_name: "",
  phone_number: "+7",
});

// Phone number formatting with debounce
const onPhoneBlur = () => {
  state.phone_number = formatPhoneNumber(state.phone_number);
};

// Form submission handler
const onSubmit = async (event: FormSubmitEvent<OrganizerRegistrationSchema>) => {
  const formData: OrganizerForm = {
    organizer_name: event.data.organizer_name,
    phone_number: event.data.phone_number,
  };

  await organizerStore.registerOrganizer(formData);

  if (organizerStore.registrationSuccess) {
    navigateTo("/profile");
  }
};

// Error handling using centralized composable
const apiErrorMessage = computed(() => getErrorMessage(organizerStore.error));

const showProfileLink = computed(() =>
  isErrorCode(organizerStore.error, "AUTH_USER_ALREADY_EXISTS"),
);
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
      @close="organizerStore.clearError()"
      class="mb-6"
      role="alert"
    >
      <template v-if="showProfileLink" #description>
        <NuxtLink
          to="/profile"
          class="text-primary-400 hover:text-primary-300 underline font-medium"
          :aria-label="t('register.goToProfile')"
        >
          {{ t("register.goToProfile") }}
        </NuxtLink>
      </template>
    </UAlert>

    <UCard>
      <UForm
        :schema="organizerRegistrationSchema"
        :state="state"
        @submit="onSubmit"
        class="space-y-6"
      >
        <UFormField
          :label="t('form.organizerName.label')"
          name="organizer_name"
          required
          :aria-required="true"
        >
          <UInput
            v-model="state.organizer_name"
            :placeholder="t('form.organizerName.placeholder')"
            icon="i-heroicons-building-office"
            size="lg"
            :maxlength="70"
            :aria-label="t('form.organizerName.label')"
          />
        </UFormField>

        <UFormField
          :label="t('form.phoneNumber.label')"
          name="phone_number"
          required
          :aria-required="true"
        >
          <UInput
            v-model="state.phone_number"
            :placeholder="t('form.phoneNumber.placeholder')"
            icon="i-heroicons-phone"
            size="lg"
            type="tel"
            :aria-label="t('form.phoneNumber.label')"
            @blur="onPhoneBlur"
          />
        </UFormField>

        <USeparator />

        <div class="flex flex-col gap-4">
          <UButton
            type="submit"
            :loading="organizerStore.loading"
            :disabled="organizerStore.loading"
            :aria-busy="organizerStore.loading"
            block
            size="xl"
            icon="i-heroicons-check-circle"
            :trailing="false"
          >
            {{
              organizerStore.loading
                ? t("form.submitButton.registering")
                : t("form.submitButton.register")
            }}
          </UButton>

          <div
            class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 justify-center"
            role="note"
          >
            <UIcon name="i-heroicons-shield-check" aria-hidden="true" />
            <span>{{ t("form.dataProtection") }}</span>
          </div>
        </div>
      </UForm>
    </UCard>
  </div>
</template>
