<script setup lang="ts">
import type { CompetitionForm } from '~/types/api';
import type { MilestoneInput } from '~/components/competition/form/MilestonesFormSection.vue';
import { createCompetitionSchemas } from '~/schemas/competition';
import { useCompetitionStore } from '~/stores/competition';
import { CalendarDate, Time, today, getLocalTimeZone } from '@internationalized/date';

const { t } = useI18n();
const router = useRouter();
const competitionStore = useCompetitionStore();
const toast = useToast();

// SEO Meta tags
useSeoMeta({
  title: t('seo.createCompetition.title'),
  description: t('seo.createCompetition.description'),
});

// Is team competition toggle
const isTeamCompetition = ref(true);

// Form state
const formState = reactive<CompetitionForm & { is_team: boolean }>({
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
  is_team: true,
});

// Date ranges for schedule
const registrationDateRange = ref<{ start: CalendarDate; end: CalendarDate } | undefined>(undefined);
const registrationStartTime = ref<Time | undefined>(new Time(0, 0));
const registrationEndTime = ref<Time | undefined>(new Time(0, 0));

const teamFormationDateRange = ref<{ start: CalendarDate; end: CalendarDate } | undefined>(undefined);
const teamFormationStartTime = ref<Time | undefined>(new Time(0, 0));
const teamFormationEndTime = ref<Time | undefined>(new Time(0, 0));

// Min values for date pickers
// Registration: must be today or later
const registrationMinValue = computed(() => today(getLocalTimeZone()));

// Team formation: must be after registration end date (or today if not set)
const teamFormationMinValue = computed(() => {
  if (registrationDateRange.value?.end) {
    // Day after registration end
    return registrationDateRange.value.end.add({ days: 1 });
  }
  return today(getLocalTimeZone());
});

// Watch isTeamCompetition and clear team fields when switching to individual
watch(isTeamCompetition, (isTeam) => {
  formState.is_team = isTeam;

  if (!isTeam) {
    // Clear team formation dates
    teamFormationDateRange.value = undefined;
    teamFormationStartTime.value = new Time(0, 0);
    teamFormationEndTime.value = new Time(0, 0);
    formState.schedule.team_formation_start = null;
    formState.schedule.team_formation_end = null;

    // Reset team size to defaults (will not be sent if not team competition)
    formState.team_size.min = 1;
    formState.team_size.max = 5;
  }
});

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

// Milestones
const milestones = ref<MilestoneInput[]>([]);

// Sync milestones into formState for validation
watch(milestones, () => {
  formState.milestones = getMilestonesForSubmit();
}, { deep: true });

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
    // Prepare form data with milestones (exclude is_team field)
    const { is_team, ...formDataWithoutIsTeam } = formState;
    const formData: CompetitionForm = {
      ...formDataWithoutIsTeam,
      milestones: getMilestonesForSubmit(),
    };

    // Submit (validation will be handled by UForm)
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
    // API errors (not validation errors)
    toast.add({
      title: t('errors.default.title'),
      description: error.message || t('errors.default.description'),
      icon: 'i-heroicons-exclamation-triangle',
      color: 'error',
    });
  } finally {
    isSubmitting.value = false;
  }
};

const handleError = async (event: any) => {
  const errors = event.errors || [];

  if (errors.length > 0) {
    // Show toast notification with error count
    toast.add({
      title: t('competition.create.validation.errorsFound', { count: errors.length }),
      description: t('competition.create.validation.scrollToErrors'),
      icon: 'i-heroicons-exclamation-circle',
      color: 'error',
    });

    // Scroll to first error field
    await nextTick();
    const firstErrorElement = document.getElementById(errors[0].id);
    if (firstErrorElement) {
      firstErrorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
      firstErrorElement.focus();
    }
  }
};

const goBack = () => {
  router.push('/competitions');
};
</script>

<template>
  <UPage>
    <UPageBody>
      <UContainer class="!max-w-4xl">
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
        <UForm
          :state="formState"
          :schema="schemas.competitionFormSchema"
          @submit="handleSubmit"
          @error="handleError"
          class="space-y-6"
        >
          <!-- Cards Grid - Two columns on large screens -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Basic Information -->
            <CompetitionFormBasicInfoFormSection
              v-model:title="formState.title"
              v-model:description="formState.description"
              v-model:domains="formState.domains"
              v-model:participant-type="formState.participant_type"
              v-model:is-team-competition="isTeamCompetition"
            />

            <!-- Schedule -->
            <CompetitionFormScheduleFormSection
              v-model:registration-date-range="registrationDateRange"
              v-model:registration-start-time="registrationStartTime"
              v-model:registration-end-time="registrationEndTime"
              v-model:team-formation-date-range="teamFormationDateRange"
              v-model:team-formation-start-time="teamFormationStartTime"
              v-model:team-formation-end-time="teamFormationEndTime"
              :is-team-competition="isTeamCompetition"
              :registration-min-value="registrationMinValue"
              :team-formation-min-value="teamFormationMinValue"
            />

            <!-- Participants -->
            <CompetitionFormParticipantsFormSection
              v-model:participant-limits-min="formState.participant_limits.min"
              v-model:participant-limits-max="formState.participant_limits.max"
              v-model:team-size-min="formState.team_size.min"
              v-model:team-size-max="formState.team_size.max"
              :is-team-competition="isTeamCompetition"
            />

            <!-- Venue -->
            <CompetitionFormVenueFormSection
              v-model:format="formState.venue.format"
              v-model:location="formState.venue.location"
            />

            <!-- Milestones -->
            <CompetitionFormMilestonesFormSection
              v-model:milestones="milestones"
              @add-milestone="addMilestone"
              @remove-milestone="removeMilestone"
            />
          </div>

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
        </UForm>
      </UContainer>
    </UPageBody>
  </UPage>
</template>
