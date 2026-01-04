<script setup lang="ts">
import type { CompetitionForm, Domain, ParticipantType, CompetitionFormat } from '~/types/api';
import { createCompetitionSchemas } from '~/schemas/competition';
import { useCompetitionStore } from '~/stores/competition';
import { CalendarDate, Time } from '@internationalized/date';

const { t } = useI18n();
const router = useRouter();
const competitionStore = useCompetitionStore();
const toast = useToast();

// SEO Meta tags
useSeoMeta({
  title: t('seo.createCompetition.title'),
  description: t('seo.createCompetition.description'),
});

// Form state
const formState = reactive<CompetitionForm>({
  title: '',
  description: '',
  schedule: {
    registration_start: '',
    registration_end: '',
    team_formation_start: null,
    team_formation_end: null,
  },
  participant_limits: {
    min: 1,
    max: 100,
  },
  domains: [],
  participant_type: 'any',
  venue: {
    format: 'online',
    location: null,
  },
  team_size: {
    min: 1,
    max: 5,
  },
  milestones: [],
});

// Date ranges for schedule
const registrationDateRange = ref<{ start: CalendarDate; end: CalendarDate } | undefined>(undefined);
const registrationStartTime = ref<Time | undefined>(new Time(0, 0));
const registrationEndTime = ref<Time | undefined>(new Time(0, 0));

const teamFormationDateRange = ref<{ start: CalendarDate; end: CalendarDate } | undefined>(undefined);
const teamFormationStartTime = ref<Time | undefined>(new Time(0, 0));
const teamFormationEndTime = ref<Time | undefined>(new Time(0, 0));

// Helper function to combine date and time into ISO string
const combineDateTime = (date: any, time: any): string => {
  if (!date) return '';
  const hour = time?.hour ?? 0;
  const minute = time?.minute ?? 0;
  return new Date(date.year, date.month - 1, date.day, hour, minute).toISOString();
};

// Watch date range and time changes for registration
watch([registrationDateRange, registrationStartTime, registrationEndTime], () => {
  if (registrationDateRange.value?.start) {
    formState.schedule.registration_start = combineDateTime(registrationDateRange.value.start, registrationStartTime.value);
  }
  if (registrationDateRange.value?.end) {
    formState.schedule.registration_end = combineDateTime(registrationDateRange.value.end, registrationEndTime.value);
  }
});

// Watch date range and time changes for team formation
watch([teamFormationDateRange, teamFormationStartTime, teamFormationEndTime], () => {
  if (teamFormationDateRange.value?.start) {
    formState.schedule.team_formation_start = combineDateTime(teamFormationDateRange.value.start, teamFormationStartTime.value);
  } else {
    formState.schedule.team_formation_start = null;
  }

  if (teamFormationDateRange.value?.end) {
    formState.schedule.team_formation_end = combineDateTime(teamFormationDateRange.value.end, teamFormationEndTime.value);
  } else {
    formState.schedule.team_formation_end = null;
  }
});

// Validation schemas
const schemas = createCompetitionSchemas(t);

// Domain options
const domainOptions = [
  { value: 'frontend' as Domain, label: t('competition.form.domains.options.frontend') },
  { value: 'mobile' as Domain, label: t('competition.form.domains.options.mobile') },
  { value: 'backend' as Domain, label: t('competition.form.domains.options.backend') },
  { value: 'ai' as Domain, label: t('competition.form.domains.options.ai') },
  { value: 'devops' as Domain, label: t('competition.form.domains.options.devops') },
];

// Participant type options
const participantTypeOptions = [
  { value: 'schoolchild' as ParticipantType, label: t('competition.form.participantType.options.schoolchild') },
  { value: 'student' as ParticipantType, label: t('competition.form.participantType.options.student') },
  { value: 'any' as ParticipantType, label: t('competition.form.participantType.options.any') },
];

// Venue format options
const venueFormatOptions = [
  { value: 'online' as CompetitionFormat, label: t('competition.form.venue.format.options.online') },
  { value: 'offline' as CompetitionFormat, label: t('competition.form.venue.format.options.offline') },
  { value: 'hybrid' as CompetitionFormat, label: t('competition.form.venue.format.options.hybrid') },
];

// Milestone management
interface MilestoneInput {
  title: string;
  date: CalendarDate | undefined;
  time: Time | undefined;
}

const milestones = ref<MilestoneInput[]>([]);

const addMilestone = () => {
  milestones.value.push({
    title: '',
    date: undefined,
    time: new Time(0, 0)
  });
};

const removeMilestone = (index: number) => {
  milestones.value.splice(index, 1);
};

// Convert milestones to the format expected by the API
const getMilestonesForSubmit = (): Array<{ title: string; timestamp: string }> => {
  return milestones.value
    .filter(m => m.title && m.date)
    .map(m => ({
      title: m.title,
      timestamp: combineDateTime(m.date, m.time)
    })) as Array<{ title: string; timestamp: string }>;
};

// Form submission
const isSubmitting = ref(false);

const handleSubmit = async () => {
  isSubmitting.value = true;

  try {
    // Prepare form data
    const formData: CompetitionForm = {
      ...formState,
      milestones: getMilestonesForSubmit(),
    };

    // Validate
    await schemas.competitionFormSchema.parseAsync(formData);

    // Submit
    await competitionStore.createCompetition(formData);

    if (competitionStore.creationSuccess) {
      // Redirect to competitions list
      router.push('/competitions');
    } else if (competitionStore.error) {
      toast.add({
        title: t('errors.default.title'),
        description: competitionStore.error.message,
        icon: 'i-heroicons-exclamation-triangle',
        color: 'error',
      });
    }
  } catch (error: any) {
    toast.add({
      title: t('apiErrors.VALIDATION_ERROR'),
      description: error.message || t('errors.default.description'),
      icon: 'i-heroicons-exclamation-triangle',
      color: 'error',
    });
  } finally {
    isSubmitting.value = false;
  }
};

const goBack = () => {
  router.push('/competitions');
};
</script>

<template>
  <UPage>
    <UPageBody>
      <div class="max-w-4xl mx-auto">
        <!-- Header -->
        <div class="mb-8">
          <UButton
            icon="i-heroicons-arrow-left"
            variant="ghost"
            color="neutral"
            :label="t('competition.create.backButton')"
            @click="goBack"
            class="mb-4"
          />
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {{ t('competition.create.title') }}
          </h1>
          <p class="text-gray-600 dark:text-gray-400">
            {{ t('competition.create.description') }}
          </p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Basic Information -->
          <UCard>
            <template #header>
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                {{ t('competition.create.sections.basic') }}
              </h2>
            </template>

            <div class="space-y-6">
              <!-- Title -->
              <UFormField
                :label="t('competition.form.title.label')"
                required
                size="xl"
              >
                <UInput
                  v-model="formState.title"
                  :placeholder="t('competition.form.title.placeholder')"
                  size="xl"
                  class="w-full text-lg"
                />
              </UFormField>

              <!-- Description -->
              <UFormField
                :label="t('competition.form.description.label')"
                required
                size="xl"
              >
                <UTextarea
                  v-model="formState.description"
                  :placeholder="t('competition.form.description.placeholder')"
                  :rows="6"
                  size="xl"
                  class="w-full text-lg"
                />
              </UFormField>

              <!-- Domains -->
              <UFormField
                :label="t('competition.form.domains.label')"
                required
                size="xl"
              >
                <UCheckboxGroup
                  v-model="formState.domains"
                  :items="domainOptions"
                  orientation="horizontal"
                  size="xl"
                />
              </UFormField>

              <!-- Participant Type -->
              <UFormField
                :label="t('competition.form.participantType.label')"
                required
                size="xl"
              >
                <URadioGroup
                  v-model="formState.participant_type"
                  :items="participantTypeOptions"
                  size="xl"
                />
              </UFormField>
            </div>
          </UCard>

          <!-- Schedule -->
          <UCard>
            <template #header>
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                {{ t('competition.create.sections.schedule') }}
              </h2>
            </template>

            <div class="space-y-6">
              <!-- Registration Period -->
              <div>
                <UFormField
                  :label="t('competition.form.schedule.registrationPeriod.label')"
                  required
                  size="xl"
                  class="mb-3"
                >
                  <UInputDate
                    :model-value="(registrationDateRange as any)"
                    @update:model-value="(val: any) => registrationDateRange = val"
                    range
                    size="xl"
                  />
                </UFormField>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
                  <UFormField
                    :label="t('competition.form.schedule.startTime.label')"
                    size="lg"
                  >
                    <UInputTime
                      :model-value="(registrationStartTime as any)"
                      @update:model-value="(val: any) => registrationStartTime = val"
                      size="xl"
                      :hour-cycle="24"
                      leading-icon="i-heroicons-clock"
                    />
                  </UFormField>

                  <UFormField
                    :label="t('competition.form.schedule.endTime.label')"
                    size="lg"
                  >
                    <UInputTime
                      :model-value="(registrationEndTime as any)"
                      @update:model-value="(val: any) => registrationEndTime = val"
                      size="xl"
                      :hour-cycle="24"
                      leading-icon="i-heroicons-clock"
                    />
                  </UFormField>
                </div>
              </div>

              <!-- Team Formation Period -->
              <div>
                <UFormField
                  :label="t('competition.form.schedule.teamFormationPeriod.label')"
                  size="xl"
                  class="mb-3"
                >
                  <UInputDate
                    :model-value="(teamFormationDateRange as any)"
                    @update:model-value="(val: any) => teamFormationDateRange = val"
                    range
                    size="xl"
                  />
                </UFormField>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
                  <UFormField
                    :label="t('competition.form.schedule.startTime.label')"
                    size="lg"
                  >
                    <UInputTime
                      :model-value="(teamFormationStartTime as any)"
                      @update:model-value="(val: any) => teamFormationStartTime = val"
                      size="xl"
                      :hour-cycle="24"
                      leading-icon="i-heroicons-clock"
                    />
                  </UFormField>

                  <UFormField
                    :label="t('competition.form.schedule.endTime.label')"
                    size="lg"
                  >
                    <UInputTime
                      :model-value="(teamFormationEndTime as any)"
                      @update:model-value="(val: any) => teamFormationEndTime = val"
                      size="xl"
                      :hour-cycle="24"
                      leading-icon="i-heroicons-clock"
                    />
                  </UFormField>
                </div>
              </div>
            </div>
          </UCard>

          <!-- Participants -->
          <UCard>
            <template #header>
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                {{ t('competition.create.sections.participants') }}
              </h2>
            </template>

            <div class="space-y-6">
              <!-- Participant Limits -->
              <UFormField
                :label="t('competition.form.participantLimits.label')"
                required
                size="xl"
              >
                <div class="space-y-3">
                  <div class="flex justify-between text-base font-medium text-gray-700 dark:text-gray-300">
                    <span>{{ t('competition.form.participantLimits.min.label') }}: {{ formState.participant_limits.min }}</span>
                    <span>{{ t('competition.form.participantLimits.max.label') }}: {{ formState.participant_limits.max }}</span>
                  </div>
                  <USlider
                    :model-value="[formState.participant_limits.min, formState.participant_limits.max]"
                    :min="1"
                    :max="1000"
                    :step="1"
                    size="xl"
                    @update:model-value="(val) => {
                      if (val && val[0] !== undefined && val[1] !== undefined) {
                        formState.participant_limits.min = val[0];
                        formState.participant_limits.max = val[1];
                      }
                    }"
                  />
                </div>
              </UFormField>

              <!-- Team Size -->
              <UFormField
                :label="t('competition.form.teamSize.label')"
                required
                size="xl"
              >
                <div class="space-y-3">
                  <div class="flex justify-between text-base font-medium text-gray-700 dark:text-gray-300">
                    <span>{{ t('competition.form.teamSize.min.label') }}: {{ formState.team_size.min }}</span>
                    <span>{{ t('competition.form.teamSize.max.label') }}: {{ formState.team_size.max }}</span>
                  </div>
                  <USlider
                    :model-value="[formState.team_size.min, formState.team_size.max]"
                    :min="1"
                    :max="20"
                    :step="1"
                    size="xl"
                    @update:model-value="(val) => {
                      if (val && val[0] !== undefined && val[1] !== undefined) {
                        formState.team_size.min = val[0];
                        formState.team_size.max = val[1];
                      }
                    }"
                  />
                </div>
              </UFormField>
            </div>
          </UCard>

          <!-- Venue -->
          <UCard>
            <template #header>
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                {{ t('competition.create.sections.venue') }}
              </h2>
            </template>

            <div class="space-y-6">
              <!-- Format -->
              <UFormField
                :label="t('competition.form.venue.format.label')"
                required
                size="xl"
              >
                <URadioGroup
                  v-model="formState.venue.format"
                  :items="venueFormatOptions"
                  size="xl"
                />
              </UFormField>

              <!-- Location -->
              <UFormField
                v-if="formState.venue.format !== 'online'"
                :label="t('competition.form.venue.location.label')"
                size="xl"
              >
                <UInput
                  v-model="formState.venue.location"
                  :placeholder="t('competition.form.venue.location.placeholder')"
                  size="xl"
                  class="w-full text-lg"
                />
              </UFormField>
            </div>
          </UCard>

          <!-- Milestones (Optional) -->
          <UCard>
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
                      v-model="milestone.title"
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
                        @update:model-value="(val: any) => milestone.date = val"
                        size="xl"
                      />
                      <UInputTime
                        :model-value="(milestone.time as any)"
                        @update:model-value="(val: any) => milestone.time = val"
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

          <!-- Submit Button -->
          <div class="flex justify-end gap-4 pt-4">
            <UButton
              variant="outline"
              color="neutral"
              size="xl"
              :label="t('common.cancel')"
              @click="goBack"
              :disabled="isSubmitting"
            />
            <UButton
              type="submit"
              color="primary"
              size="xl"
              :label="isSubmitting ? t('competition.create.submitting') : t('competition.create.submitButton')"
              :loading="isSubmitting"
              :disabled="isSubmitting"
            />
          </div>
        </form>
      </div>
    </UPageBody>
  </UPage>
</template>
