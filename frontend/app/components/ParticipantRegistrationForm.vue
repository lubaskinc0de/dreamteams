<script setup lang="ts">
import type { FormSubmitEvent } from "#ui/types";
import type { ParticipantForm, Domain, ExperienceLevel, SkillLevel } from "~/types/api";
import {
  createParticipantSchemas,
  type ParticipantRegistrationSchema,
} from "~/schemas/participant";
import { useNotificationsStore } from "~/stores/notifications";
import { useParticipantStore } from "~/stores/participant";

interface SkillState { name: string; level: string }
interface ContactState { title: string; url: string }

const participantStore = useParticipantStore();
const { getErrorMessage, isErrorCode } = useErrorHandler();
const { t } = useI18n();
const api = useApi();
const notifications = useNotificationsStore();

const state = reactive({
  full_name: "",
  bio: "",
  experience_level: "" as string,
  preferred_domains: [] as Domain[],
  skills: [{ name: "", level: "" }] as SkillState[],
  contacts: [] as ContactState[],
});

const {
  participantRegistrationSchema,
} = createParticipantSchemas(t);

// Avatar upload state
const selectedAvatar = ref<File | null>(null);
const isUploadingAvatar = ref(false);
const avatarUploadError = ref<string | null>(null);

const handleAvatarUpload = async (file: File) => {
  selectedAvatar.value = file;
  avatarUploadError.value = null;
};

const handleAvatarDelete = () => {
  selectedAvatar.value = null;
  avatarUploadError.value = null;
};

// Skills management
const addSkill = () => {
  state.skills.push({ name: "", level: "" });
};

const removeSkill = (index: number) => {
  state.skills.splice(index, 1);
};

// Contacts management
const addContact = () => {
  state.contacts.push({ title: "", url: "" });
};

const removeContact = (index: number) => {
  state.contacts.splice(index, 1);
};

const experienceLevelOptions = computed(() => [
  { value: "JUNIOR", label: t("form.experienceLevel.options.JUNIOR") },
  { value: "MID", label: t("form.experienceLevel.options.MID") },
  { value: "SENIOR", label: t("form.experienceLevel.options.SENIOR") },
]);

const skillLevelOptions = computed(() => [
  { value: "BEGINNER", label: t("form.skills.options.BEGINNER") },
  { value: "INTERMEDIATE", label: t("form.skills.options.INTERMEDIATE") },
  { value: "ADVANCED", label: t("form.skills.options.ADVANCED") },
  { value: "EXPERT", label: t("form.skills.options.EXPERT") },
]);

const domainOptions = computed(() => [
  { value: "frontend", label: t("competition.form.domains.options.frontend") },
  { value: "mobile", label: t("competition.form.domains.options.mobile") },
  { value: "backend", label: t("competition.form.domains.options.backend") },
  { value: "ai", label: t("competition.form.domains.options.ai") },
  { value: "devops", label: t("competition.form.domains.options.devops") },
]);

// Form submission handler
const onSubmit = async (event: FormSubmitEvent<ParticipantRegistrationSchema>) => {
  const formData: ParticipantForm = {
    full_name: event.data.full_name,
    bio: event.data.bio,
    experience_level: event.data.experience_level,
    preferred_domains: event.data.preferred_domains,
    skills: event.data.skills.map((s) => ({ name: s.name, level: s.level })),
    contacts: event.data.contacts.map((c) => ({ title: c.title, url: c.url })),
  };

  await participantStore.registerParticipant(formData);

  if (participantStore.registrationSuccess && selectedAvatar.value) {
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
      <UFormField :label="t('form.fullName.label')" name="full_name" required :aria-required="true" class="w-full">
        <UInput
          v-model="state.full_name"
          :placeholder="t('form.fullName.placeholder')"
          icon="i-heroicons-user"
          size="xl"
          :maxlength="70"
          :aria-label="t('form.fullName.label')"
          class="w-full"
        />
      </UFormField>

      <!-- Bio -->
      <UFormField :label="t('form.bio.label')" name="bio" class="w-full">
        <UTextarea
          v-model="state.bio"
          :placeholder="t('form.bio.placeholder')"
          size="xl"
          :maxlength="500"
          :rows="4"
          :aria-label="t('form.bio.label')"
          class="w-full"
        />
      </UFormField>

      <!-- Experience Level -->
      <UFormField :label="t('form.experienceLevel.label')" name="experience_level" required :aria-required="true" class="w-full">
        <USelect
          v-model="state.experience_level"
          :items="experienceLevelOptions"
          value-key="value"
          size="xl"
          :placeholder="t('form.experienceLevel.label')"
          :aria-label="t('form.experienceLevel.label')"
          class="w-full"
        />
      </UFormField>

      <!-- Preferred Domains -->
      <UFormField :label="t('form.preferredDomains.label')" name="preferred_domains" required :aria-required="true" class="w-full">
        <USelectMenu
          v-model="state.preferred_domains"
          :items="domainOptions"
          value-key="value"
          multiple
          size="xl"
          :placeholder="t('form.preferredDomains.placeholder')"
          :aria-label="t('form.preferredDomains.label')"
          class="w-full"
        />
      </UFormField>

      <!-- Skills -->
      <UFormField :label="t('form.skills.label')" name="skills" required :aria-required="true" class="w-full">
        <div class="space-y-3">
          <div
            v-for="(skill, index) in state.skills"
            :key="index"
            class="flex gap-2 items-start"
          >
            <UInput
              v-model="skill.name"
              :placeholder="t('form.skills.namePlaceholder')"
              size="xl"
              :maxlength="70"
              :aria-label="t('form.skills.nameLabel')"
              class="flex-1"
            />
            <USelect
              v-model="skill.level"
              :items="skillLevelOptions"
              value-key="value"
              size="xl"
              :placeholder="t('form.skills.levelLabel')"
              :aria-label="t('form.skills.levelLabel')"
              class="flex-1"
            />
            <UButton
              v-if="state.skills.length > 1"
              @click="removeSkill(index)"
              icon="i-heroicons-trash"
              color="neutral"
              variant="ghost"
              size="xl"
              :aria-label="t('common.remove')"
            />
          </div>
          <UButton
            @click="addSkill"
            icon="i-heroicons-plus"
            color="primary"
            variant="ghost"
            size="sm"
          >
            {{ t("form.skills.addButton") }}
          </UButton>
        </div>
      </UFormField>

      <!-- Contacts (optional) -->
      <UFormField :label="t('form.contacts.label')" name="contacts" class="w-full">
        <div class="space-y-3">
          <div
            v-for="(contact, index) in state.contacts"
            :key="index"
            class="flex gap-2 items-start"
          >
            <UInput
              v-model="contact.title"
              :placeholder="t('form.contacts.titlePlaceholder')"
              size="xl"
              :maxlength="70"
              :aria-label="t('form.contacts.titleLabel')"
              class="flex-1"
            />
            <UInput
              v-model="contact.url"
              :placeholder="t('form.contacts.urlPlaceholder')"
              size="xl"
              type="url"
              :aria-label="t('form.contacts.urlLabel')"
              class="flex-1"
            />
            <UButton
              @click="removeContact(index)"
              icon="i-heroicons-trash"
              color="neutral"
              variant="ghost"
              size="xl"
              :aria-label="t('common.remove')"
            />
          </div>
          <UButton
            @click="addContact"
            icon="i-heroicons-plus"
            color="primary"
            variant="ghost"
            size="sm"
          >
            {{ t("form.contacts.addButton") }}
          </UButton>
        </div>
      </UFormField>

      <div class="pt-2">
        <UButton
          type="submit"
          :loading="isLoading"
          :disabled="isLoading"
          :aria-busy="isLoading"
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

        <div class="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400 justify-center mt-3" role="note">
          <UIcon name="i-heroicons-shield-check" aria-hidden="true" />
          <span>{{ t("form.dataProtection") }}</span>
        </div>
      </div>
    </UForm>
  </div>
</template>
