<script setup lang="ts">
import type { ExperienceLevel, UpdateParticipantForm } from "~/types/api";
import { useParticipantStore } from "~/stores/participant";

type EditableField = "bio" | "experience_level" | "skills" | "contacts";
type SkillLevel = "BEGINNER" | "INTERMEDIATE" | "ADVANCED" | "EXPERT";

const props = defineProps<{ open: boolean; field: EditableField }>();
const emit = defineEmits<{ "update:open": [boolean] }>();

const { t } = useI18n();
const participantStore = useParticipantStore();
const userStore = useUserStore();
const { getErrorMessage } = useErrorHandler();

const fieldTitleKey: Record<EditableField, string> = {
  bio: "profile.participant.bio",
  experience_level: "profile.participant.experienceLevel",
  skills: "profile.participant.skills",
  contacts: "profile.participant.contacts",
};

const title = computed(() => t(fieldTitleKey[props.field]));

// Local state for each field type
const bio = ref("");
const experienceLevel = ref<ExperienceLevel | null>(null);
const skills = ref<{ name: string; level: SkillLevel }[]>([]);
const contacts = ref<{ title: string; value: string }[]>([]);

const reset = () => {
  const p = userStore.participant;
  if (!p) return;
  bio.value = p.bio ?? "";
  experienceLevel.value = p.experience_level ?? null;
  skills.value = p.skills.map((s) => ({ name: s.name, level: s.level as SkillLevel }));
  contacts.value = p.contacts.map((c) => ({ title: c.title, value: c.value }));
  participantStore.clearError();
};

watch(() => props.open, (v) => { if (v) reset(); });

// Options
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

const addSkill = () => { skills.value.push({ name: "", level: "BEGINNER" }); };
const removeSkill = (i: number) => { skills.value.splice(i, 1); };
const addContact = () => {
  if (contacts.value.length < 15) contacts.value.push({ title: "", value: "" });
};
const removeContact = (i: number) => { contacts.value.splice(i, 1); };

const onSave = async () => {
  const p = userStore.participant;
  if (!p) return;

  const form: UpdateParticipantForm = {
    full_name: p.full_name,
    participant_type: p.participant_type,
    age: p.age,
    bio: p.bio,
    skills: p.skills,
    experience_level: p.experience_level,
    contacts: p.contacts,
  };

  if (props.field === "bio") form.bio = bio.value.trim() || null;
  else if (props.field === "experience_level") form.experience_level = experienceLevel.value;
  else if (props.field === "skills") form.skills = skills.value;
  else if (props.field === "contacts") form.contacts = contacts.value;

  await participantStore.updateParticipant(form);
  if (participantStore.updateSuccess) emit("update:open", false);
};

const apiError = computed(() => getErrorMessage(participantStore.error));
</script>

<template>
  <UModal :open="open" @update:open="$emit('update:open', $event)">
    <template #content>
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-base font-semibold">{{ title }}</h3>
            <UButton icon="i-heroicons-x-mark" color="neutral" variant="ghost" @click="$emit('update:open', false)" />
          </div>
        </template>

        <UAlert
          v-if="apiError"
          color="error"
          variant="soft"
          :title="apiError"
          icon="i-heroicons-exclamation-circle"
          :close-button="{ icon: 'i-heroicons-x-mark-20-solid', color: 'neutral', variant: 'ghost', padded: false }"
          @close="participantStore.clearError()"
          class="mb-4"
        />

        <!-- Bio -->
        <UTextarea
          v-if="field === 'bio'"
          v-model="bio"
          :placeholder="t('form.bio.placeholder')"
          :maxlength="500"
          :rows="4"
          class="w-full"
        />

        <!-- Experience Level -->
        <USelect
          v-else-if="field === 'experience_level'"
          v-model="experienceLevel"
          :items="experienceLevelOptions"
          value-key="value"
          size="xl"
          class="w-full"
        />

        <!-- Skills -->
        <div v-else-if="field === 'skills'" class="space-y-2">
          <div v-for="(skill, i) in skills" :key="i" class="flex gap-2 items-center">
            <UInput v-model="skill.name" :placeholder="t('form.skills.namePlaceholder')" size="sm" class="flex-1" />
            <USelect v-model="skill.level" :items="skillLevelOptions" value-key="value" size="sm" class="w-36" />
            <UButton icon="i-heroicons-trash" color="error" variant="ghost" size="sm" type="button" @click="removeSkill(i)" />
          </div>
          <UButton icon="i-heroicons-plus" color="neutral" variant="ghost" size="sm" type="button" @click="addSkill">
            {{ t("form.skills.addButton") }}
          </UButton>
        </div>

        <!-- Contacts -->
        <div v-else-if="field === 'contacts'" class="space-y-2">
          <div v-for="(contact, i) in contacts" :key="i" class="flex gap-2 items-center">
            <UInput v-model="contact.title" :placeholder="t('form.contacts.titlePlaceholder')" size="sm" class="w-32" />
            <UInput v-model="contact.value" :placeholder="t('form.contacts.valuePlaceholder')" size="sm" class="flex-1" />
            <UButton icon="i-heroicons-trash" color="error" variant="ghost" size="sm" type="button" @click="removeContact(i)" />
          </div>
          <UButton icon="i-heroicons-plus" color="neutral" variant="ghost" size="sm" type="button" :disabled="contacts.length >= 15" @click="addContact">
            {{ t("form.contacts.addButton") }}
          </UButton>
        </div>

        <div class="flex justify-end gap-3 pt-4">
          <UButton color="neutral" variant="ghost" @click="$emit('update:open', false)">
            {{ t("common.cancel") }}
          </UButton>
          <UButton :loading="participantStore.loading" icon="i-heroicons-check" @click="onSave">
            {{ t("common.save") }}
          </UButton>
        </div>
      </UCard>
    </template>
  </UModal>
</template>
