<script setup lang="ts">
import type { CompetitionTag, CompetitionTrack, ParticipantType } from '~/types/api';

/**
 * Секция формы с базовой информацией о соревновании
 */

interface Props {
  title: string;
  description: string;
  tagIds: string[];
  tracks: CompetitionTrack[];
  initialTags?: CompetitionTag[];
  participantType: ParticipantType;
  isTeamCompetition: boolean;
  autoAccept?: boolean;
  isArchived?: boolean;
  showArchiveField?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  showArchiveField: false,
  autoAccept: false,
  initialTags: () => [],
});
const emit = defineEmits(['update:title', 'update:description', 'update:tagIds', 'update:tracks', 'update:participantType', 'update:isTeamCompetition', 'update:autoAccept', 'update:isArchived']);

const { t } = useI18n();

const availableTags = ref<CompetitionTag[]>([...props.initialTags]);
const selectedTagCache = ref<CompetitionTag[]>([...props.initialTags]);
const tagSearch = ref("");
const tagsLoading = ref(false);
const tagPickerOpen = ref(false);
let tagSearchTimer: ReturnType<typeof setTimeout> | null = null;

const mergedTags = computed(() => {
  const byId = new Map<string, CompetitionTag>();
  for (const tag of props.initialTags) byId.set(tag.id, tag);
  for (const tag of selectedTagCache.value) byId.set(tag.id, tag);
  for (const tag of availableTags.value) byId.set(tag.id, tag);
  return [...byId.values()].sort((a, b) => a.value.localeCompare(b.value));
});

const selectedTags = computed(() =>
  mergedTags.value.filter((tag) => props.tagIds.includes(tag.id)),
);

const fetchTags = async () => {
  tagsLoading.value = true;
  const api = useApi();
  const { data } = await api.listTags({
    page: 1,
    search: tagSearch.value.trim() || undefined,
  });
  if (data) {
    availableTags.value = data.items;
  }
  tagsLoading.value = false;
};

watch(tagSearch, () => {
  if (tagSearchTimer) clearTimeout(tagSearchTimer);
  tagSearchTimer = setTimeout(fetchTags, 250);
});

onMounted(fetchTags);

onBeforeUnmount(() => {
  if (tagSearchTimer) clearTimeout(tagSearchTimer);
});

const toggleTag = (tagId: string, checked: boolean) => {
  if (checked) {
    const tag = mergedTags.value.find((item) => item.id === tagId);
    if (tag && !selectedTagCache.value.some((item) => item.id === tag.id)) {
      selectedTagCache.value = [...selectedTagCache.value, tag];
    }
  }
  const next = checked
    ? [...new Set([...props.tagIds, tagId])]
    : props.tagIds.filter((id) => id !== tagId);
  emit('update:tagIds', next);
};

const removeTag = (tagId: string) => {
  toggleTag(tagId, false);
};

const addTrack = () => {
  emit('update:tracks', [...props.tracks, { name: '' }]);
};

const updateTrack = (index: number, name: string) => {
  emit('update:tracks', props.tracks.map((track, i) => (i === index ? { name } : track)));
};

const removeTrack = (index: number) => {
  emit('update:tracks', props.tracks.filter((_, i) => i !== index));
};

// Participant type options
const participantTypeOptions = [
  { value: 'schoolchild' as ParticipantType, label: t('competition.form.participantType.options.schoolchild') },
  { value: 'student' as ParticipantType, label: t('competition.form.participantType.options.student') },
  { value: 'any' as ParticipantType, label: t('competition.form.participantType.options.any') },
];
</script>

<template>
  <UCard class="lg:col-span-2">
    <template #header>
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
        {{ t('competition.create.sections.basic') }}
      </h2>
    </template>

    <div class="space-y-6">
      <!-- Title -->
      <UFormField name="title" required size="xl">
        <template #label>
          {{ t('competition.form.title.label') }}
          <HelpTooltip :text="t('competition.form.title.tooltip')" />
        </template>
        <UInput
          :model-value="title"
          @update:model-value="emit('update:title', $event)"
          :placeholder="t('competition.form.title.placeholder')"
          size="xl"
          class="w-full text-lg"
        />
      </UFormField>

      <!-- Description -->
      <UFormField name="description" required size="xl">
        <template #label>
          {{ t('competition.form.description.label') }}
          <HelpTooltip :text="t('competition.form.description.tooltip')" />
        </template>
        <UTextarea
          :model-value="description"
          @update:model-value="emit('update:description', $event)"
          :placeholder="t('competition.form.description.placeholder')"
          :rows="6"
          size="xl"
          class="w-full text-lg"
        />
      </UFormField>

      <!-- Tags -->
      <UFormField name="tag_ids" size="xl">
        <template #label>
          {{ t('competition.form.tags.label') }}
          <HelpTooltip :text="t('competition.form.tags.tooltip')" />
        </template>
        <div class="flex flex-wrap items-center gap-2">
          <UButton
            v-for="tag in selectedTags"
            :key="tag.id"
            type="button"
            color="primary"
            variant="soft"
            size="sm"
            trailing-icon="i-heroicons-x-mark"
            :label="tag.value"
            @click="removeTag(tag.id)"
          />

          <UPopover v-model:open="tagPickerOpen">
            <UButton
              type="button"
              icon="i-heroicons-plus"
              color="neutral"
              variant="outline"
              size="sm"
              :aria-label="t('competition.form.tags.add')"
            />

            <template #content>
              <div class="w-72 p-3 space-y-3">
                <UInput
                  v-model="tagSearch"
                  icon="i-heroicons-magnifying-glass"
                  :placeholder="t('competition.form.tags.placeholder')"
                  class="w-full"
                  autofocus
                />
                <div v-if="tagsLoading" class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                  <UIcon name="i-heroicons-arrow-path" class="animate-spin" />
                  {{ t('common.loading') }}
                </div>
                <div v-else-if="mergedTags.length" class="max-h-64 overflow-y-auto space-y-2 pr-1">
                  <UCheckbox
                    v-for="tag in mergedTags"
                    :key="tag.id"
                    :label="tag.value"
                    :model-value="tagIds.includes(tag.id)"
                    @update:model-value="(checked) => toggleTag(tag.id, Boolean(checked))"
                  />
                </div>
                <p v-else class="text-sm text-gray-500 dark:text-gray-400">
                  {{ t('competition.form.tags.empty') }}
                </p>
              </div>
            </template>
          </UPopover>
        </div>
      </UFormField>

      <!-- Tracks -->
      <UFormField name="tracks" required size="xl">
        <template #label>
          {{ t('competition.form.tracks.label') }}
          <HelpTooltip :text="t('competition.form.tracks.tooltip')" />
        </template>
        <div class="space-y-2">
          <div
            v-for="(track, index) in tracks"
            :key="index"
            class="flex gap-2"
          >
            <UInput
              :model-value="track.name"
              @update:model-value="(value) => updateTrack(index, String(value))"
              :placeholder="t('competition.form.tracks.placeholder')"
              :maxlength="100"
              class="flex-1"
            />
            <UButton
              icon="i-heroicons-trash"
              color="error"
              variant="ghost"
              square
              :aria-label="t('competition.form.tracks.remove')"
              :disabled="tracks.length <= 1"
              @click="removeTrack(index)"
            />
          </div>
          <UButton
            icon="i-heroicons-plus"
            color="neutral"
            variant="ghost"
            type="button"
            :label="t('competition.form.tracks.add')"
            @click="addTrack"
          />
        </div>
      </UFormField>

      <!-- Participant Type -->
      <UFormField name="participant_type" required size="xl">
        <template #label>
          {{ t('competition.form.participantType.label') }}
          <HelpTooltip :text="t('competition.form.participantType.tooltip')" />
        </template>
        <URadioGroup
          :model-value="participantType"
          @update:model-value="emit('update:participantType', $event)"
          :items="participantTypeOptions"
          size="xl"
        />
      </UFormField>

      <!-- Is Team Competition -->
      <UFormField size="xl">
        <template #label>
          {{ t('competition.form.isTeam.label') }}
          <HelpTooltip :text="t('competition.form.isTeam.tooltip')" />
        </template>
        <div class="flex items-center gap-3">
          <USwitch
            :model-value="isTeamCompetition"
            @update:model-value="emit('update:isTeamCompetition', $event)"
            size="xl"
          />
          <span class="text-gray-700 dark:text-gray-300">{{ t('competition.form.isTeam.checkboxLabel') }}</span>
        </div>
      </UFormField>

      <!-- Auto Accept -->
      <UFormField name="auto_accept" size="xl">
        <template #label>
          {{ t('competition.form.autoAccept.label') }}
          <HelpTooltip :text="t('competition.form.autoAccept.tooltip')" />
        </template>
        <div class="flex items-center gap-3">
          <USwitch
            :model-value="autoAccept"
            @update:model-value="emit('update:autoAccept', $event)"
            size="xl"
          />
          <span class="text-gray-700 dark:text-gray-300">{{ t('competition.form.autoAccept.checkboxLabel') }}</span>
        </div>
      </UFormField>

      <!-- Is Archived (only in edit mode) -->
      <UFormField
        v-if="showArchiveField"
        :label="t('competition.form.isArchived.label')"
        size="xl"
      >
        <div class="flex items-center gap-3">
          <USwitch
            :model-value="isArchived"
            @update:model-value="emit('update:isArchived', $event)"
            size="xl"
          />
          <span class="text-gray-700 dark:text-gray-300">{{ t('competition.form.isArchived.checkboxLabel') }}</span>
        </div>
      </UFormField>
    </div>
  </UCard>
</template>
