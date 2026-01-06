<script setup lang="ts">
/**
 * Секция формы с вехами соревнования
 */

export interface MilestoneInput {
  title: string;
  date: any;
  time: any;
}

interface Props {
  milestones: MilestoneInput[];
}

const props = defineProps<Props>();
const emit = defineEmits(['update:milestones', 'add-milestone', 'remove-milestone']);

const { t } = useI18n();

const addMilestone = () => {
  emit('add-milestone');
};

const removeMilestone = (index: number) => {
  emit('remove-milestone', index);
};

const updateMilestone = (index: number, field: keyof MilestoneInput, value: any) => {
  const updated = [...props.milestones];
  updated[index] = { ...updated[index], [field]: value } as MilestoneInput;
  emit('update:milestones', updated);
};
</script>

<template>
  <UCard class="lg:col-span-2">
    <template #header>
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
          {{ t('competition.create.sections.milestones') }}
        </h2>
        <UButton
          icon="i-heroicons-plus"
          variant="soft"
          size="sm"
          :label="t('competition.form.milestone.addButton')"
          @click="addMilestone"
        />
      </div>
    </template>

    <div v-if="milestones.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400 text-lg">
      {{ t('competition.form.milestone.empty') }}
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="(milestone, index) in milestones"
        :key="index"
        class="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
      >
        <div class="space-y-4">
          <!-- Title -->
          <UFormField
            :label="t('competition.form.milestone.title.label')"
            required
            size="lg"
          >
            <UInput
              :model-value="milestone.title"
              @update:model-value="updateMilestone(index, 'title', $event)"
              :placeholder="t('competition.form.milestone.title.placeholder')"
              size="xl"
              class="w-full text-lg"
            />
          </UFormField>

          <!-- Date and Time -->
          <UFormField
            :label="t('competition.form.milestone.datetime.label')"
            required
            size="lg"
          >
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <UInputDate
                :model-value="(milestone.date as any)"
                @update:model-value="updateMilestone(index, 'date', $event)"
                size="xl"
              />
              <UInputTime
                :model-value="(milestone.time as any)"
                @update:model-value="updateMilestone(index, 'time', $event)"
                size="xl"
                :hour-cycle="24"
                leading-icon="i-heroicons-clock"
              />
            </div>
          </UFormField>

          <!-- Remove Button -->
          <div class="flex justify-end">
            <UButton
              icon="i-heroicons-trash"
              color="error"
              variant="soft"
              size="lg"
              :label="t('common.remove')"
              @click="removeMilestone(index)"
            />
          </div>
        </div>
      </div>
    </div>
  </UCard>
</template>
