<script setup lang="ts">
import type { FormSubmitEvent } from "#ui/types";
import type {
  UpdateParticipantForm,
  ParticipantRoleType,
  ExperienceLevel,
} from "~/types/api";
import { createParticipantSchemas, type ParticipantUpdateSchema } from "~/schemas/participant";
import { useParticipantStore } from "~/stores/participant";

type SkillLevel = "BEGINNER" | "INTERMEDIATE" | "ADVANCED" | "EXPERT";

interface Props {
  open: boolean;
  fullName: string;
  participantType: ParticipantRoleType;
  age: number;
  bio?: string | null;
  experienceLevel?: ExperienceLevel | null;
  skills?: { name: string; level: SkillLevel }[];
  contacts?: { title: string; value: string }[];
}

const props = defineProps<Props>();
const emit = defineEmits<{ "update:open": [value: boolean] }>();

const { t } = useI18n();
const participantStore = useParticipantStore();
const { getErrorMessage } = useErrorHandler();
const { participantUpdateSchema } = createParticipantSchemas(t);

const state = reactive({
  full_name: props.fullName,
  participant_type: props.participantType as string,
  age: props.age as number | null,
  bio: props.bio ?? "",
  experience_level: (props.experienceLevel ?? null) as ExperienceLevel | null,
  skills: [...(props.skills ?? [])].map((s) => ({ name: s.name, level: s.level })),
  contacts: [...(props.contacts ?? [])].map((c) => ({ title: c.title, value: c.value })),
});

watch(
  () => props.open,
  (val) => {
    if (val) {
      state.full_name = props.fullName;
      state.participant_type = props.participantType;
      state.age = props.age;
      state.bio = props.bio ?? "";
      state.experience_level = props.experienceLevel ?? null;
      state.skills = [...(props.skills ?? [])].map((s) => ({ name: s.name, level: s.level }));
      state.contacts = [...(props.contacts ?? [])].map((c) => ({ title: c.title, value: c.value }));
      participantStore.clearError();
    }
  },
);

const participantTypeOptions = computed(() => [
  { value: "schoolchild", label: t("form.participantType.options.SCHOOLCHILD") },
  { value: "student", label: t("form.participantType.options.STUDENT") },
]);

const experienceLevelOptions = computed(() => [
  { value: null, label: t("form.experienceLevel.options.none") },
  { value: "JUNIOR", label: t("form.experienceLevel.options.JUNIOR") },
  { value: "MID", label: t("form.experienceLevel.options.MID") },
  { value: "SENIOR", label: t("form.experienceLevel.options.SENIOR") },
]);

const skillLevelOptions = computed(() => [
  { value: "BEGINNER", label: t("profile.participant.skillLevels.BEGINNER") },
  { value: "INTERMEDIATE", label: t("profile.participant.skillLevels.INTERMEDIATE") },
  { value: "ADVANCED", label: t("profile.participant.skillLevels.ADVANCED") },
  { value: "EXPERT", label: t("profile.participant.skillLevels.EXPERT") },
]);

const addSkill = () => {
  state.skills.push({ name: "", level: "BEGINNER" });
};

const removeSkill = (index: number) => {
  state.skills.splice(index, 1);
};

const addContact = () => {
  if (state.contacts.length < 15) {
    state.contacts.push({ title: "", value: "" });
  }
};

const removeContact = (index: number) => {
  state.contacts.splice(index, 1);
};

const onSubmit = async (event: FormSubmitEvent<ParticipantUpdateSchema>) => {
  const form: UpdateParticipantForm = {
    full_name: event.data.full_name,
    participant_type: event.data.participant_type as ParticipantRoleType,
    age: event.data.age,
    bio: event.data.bio || null,
    experience_level: event.data.experience_level ?? null,
    skills: event.data.skills,
    contacts: event.data.contacts,
  };
  await participantStore.updateParticipant(form);
  if (participantStore.updateSuccess) {
    emit("update:open", false);
  }
};

const apiError = computed(() => getErrorMessage(participantStore.error));
</script>

<template>
  <UModal :open="open" @update:open="$emit('update:open', $event)" :ui="{ content: 'max-w-lg' }">
    <template #content>
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold">{{ t("participant.edit.title") }}</h3>
            <UButton
              icon="i-heroicons-x-mark"
              color="neutral"
              variant="ghost"
              @click="$emit('update:open', false)"
            />
          </div>
        </template>

        <UAlert
          v-if="apiError"
          color="error"
          variant="soft"
          :title="apiError"
          icon="i-heroicons-exclamation-circle"
          :close-button="{
            icon: 'i-heroicons-x-mark-20-solid',
            color: 'neutral',
            variant: 'ghost',
            padded: false,
          }"
          @close="participantStore.clearError()"
          class="mb-4"
        />

        <UForm
          :schema="participantUpdateSchema"
          :state="(state as any)"
          @submit="onSubmit"
          :validate-on="['input', 'change']"
          class="space-y-4"
        >
          <!-- Full Name -->
          <UFormField :label="t('form.fullName.label')" name="full_name" required>
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
          <UFormField :label="t('form.age.label')" name="age" required>
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
          <UFormField :label="t('form.participantType.label')" name="participant_type" required>
            <URadioGroup
              v-model="state.participant_type"
              :items="participantTypeOptions"
              value-key="value"
              orientation="horizontal"
              size="xl"
            />
          </UFormField>

          <!-- Bio -->
          <UFormField :label="t('form.bio.label')" name="bio">
            <UTextarea
              v-model="state.bio"
              :placeholder="t('form.bio.placeholder')"
              :maxlength="500"
              :rows="3"
              class="w-full"
            />
          </UFormField>

          <!-- Experience Level -->
          <UFormField :label="t('form.experienceLevel.label')" name="experience_level">
            <USelect
              v-model="state.experience_level"
              :items="experienceLevelOptions"
              value-key="value"
              size="xl"
              class="w-full"
            />
          </UFormField>

          <!-- Skills -->
          <div>
            <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ t("form.skills.label") }}
            </p>
            <div class="space-y-2">
              <div
                v-for="(skill, i) in state.skills"
                :key="i"
                class="flex gap-2 items-start"
              >
                <UInput
                  v-model="skill.name"
                  :placeholder="t('form.skills.namePlaceholder')"
                  size="sm"
                  class="flex-1"
                />
                <USelect
                  v-model="skill.level"
                  :items="skillLevelOptions"
                  value-key="value"
                  size="sm"
                  class="w-36"
                />
                <UButton
                  icon="i-heroicons-trash"
                  color="error"
                  variant="ghost"
                  size="sm"
                  type="button"
                  @click="removeSkill(i)"
                />
              </div>
            </div>
            <UButton
              icon="i-heroicons-plus"
              color="neutral"
              variant="ghost"
              size="sm"
              type="button"
              class="mt-2"
              @click="addSkill"
            >
              {{ t("form.skills.addButton") }}
            </UButton>
          </div>

          <!-- Contacts -->
          <div>
            <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ t("form.contacts.label") }}
            </p>
            <div class="space-y-2">
              <div
                v-for="(contact, i) in state.contacts"
                :key="i"
                class="flex gap-2 items-start"
              >
                <UInput
                  v-model="contact.title"
                  :placeholder="t('form.contacts.titlePlaceholder')"
                  size="sm"
                  class="w-32"
                />
                <UInput
                  v-model="contact.value"
                  :placeholder="t('form.contacts.valuePlaceholder')"
                  size="sm"
                  class="flex-1"
                />
                <UButton
                  icon="i-heroicons-trash"
                  color="error"
                  variant="ghost"
                  size="sm"
                  type="button"
                  @click="removeContact(i)"
                />
              </div>
            </div>
            <UButton
              icon="i-heroicons-plus"
              color="neutral"
              variant="ghost"
              size="sm"
              type="button"
              class="mt-2"
              :disabled="state.contacts.length >= 15"
              @click="addContact"
            >
              {{ t("form.contacts.addButton") }}
            </UButton>
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <UButton color="neutral" variant="ghost" @click="$emit('update:open', false)">
              {{ t("common.cancel") }}
            </UButton>
            <UButton type="submit" :loading="participantStore.loading" icon="i-heroicons-check">
              {{ t("common.save") }}
            </UButton>
          </div>
        </UForm>
      </UCard>
    </template>
  </UModal>
</template>
