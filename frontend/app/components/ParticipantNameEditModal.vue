<script setup lang="ts">
import { useParticipantStore } from "~/stores/participant";

const props = defineProps<{ open: boolean; currentName: string }>();
const emit = defineEmits<{ "update:open": [boolean] }>();

const { t } = useI18n();
const participantStore = useParticipantStore();
const userStore = useUserStore();
const { getErrorMessage } = useErrorHandler();

const name = ref(props.currentName);

watch(
  () => props.open,
  (v) => {
    if (v) {
      name.value = props.currentName;
      participantStore.clearError();
    }
  },
);

const onSave = async () => {
  const p = userStore.participant;
  if (!p) return;
  await participantStore.updateParticipant({
    full_name: name.value.trim(),
    participant_type: p.participant_type,
    age: p.age,
    bio: p.bio,
    skills: p.skills,
    experience_level: p.experience_level,
    preferred_domains: p.preferred_domains,
    contacts: p.contacts,
  });
  if (participantStore.updateSuccess) emit("update:open", false);
};

const apiError = computed(() => getErrorMessage(participantStore.error));
const isValid = computed(() => name.value.trim().length > 0 && name.value.trim().length <= 70);
</script>

<template>
  <UModal :open="open" @update:open="$emit('update:open', $event)">
    <template #content>
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-base font-semibold">{{ t("form.fullName.label") }}</h3>
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

        <UInput
          v-model="name"
          :placeholder="t('form.fullName.placeholder')"
          icon="i-heroicons-user"
          size="xl"
          :maxlength="70"
          class="w-full"
          @keydown.enter.prevent="onSave"
        />

        <div class="flex justify-end gap-3 pt-4">
          <UButton color="neutral" variant="ghost" @click="$emit('update:open', false)">
            {{ t("common.cancel") }}
          </UButton>
          <UButton :loading="participantStore.loading" :disabled="!isValid" icon="i-heroicons-check" @click="onSave">
            {{ t("common.save") }}
          </UButton>
        </div>
      </UCard>
    </template>
  </UModal>
</template>
